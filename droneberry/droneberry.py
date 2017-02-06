"""Connects to pixhawk and facilitates communication with backend"""

import requests
import json
import hashlib
import datetime
import time
from select import select
from dronekit import connect

class Drone:
	def __init__(self):
		self.pixhawk = connect('/dev/cu.usbmodem1', baud = 115200) # for on mac via USB
		# self.pixhawk = connect('/dev/ttyS0', baud = 57600) # for on the raspberry PI via telem2

		# TODO: load from config
		self.api_url = "http://localhost/api"
		self.name = 'test'
		self.uid = 'DR1'
		self.auth = 'fd87dad2731a9a275c5f54f78f1f77d1'
		self.status = 'idle' # drone turns on in idle state

		#self.get_state() # flesh out the state

	#################################################################################
	# SERVER CONNECTIVITY
	#################################################################################

	# Post new drone state to server, print response
	def post_status(self):
		 payload = {
			 "uid": self.uid,
			 "auth": self.auth,
			 "state": json.dumps(self.get_state())
		 }
		 response = requests.post(self.api_url, data=payload)
		 return response

	def get(self, subset=None):
		if subset: payload = "uid={}&subset={}".format(self.uid, subset)
		else: payload = "uid={}".format(self.uid)
		return requests.get(self.api_url, params=payload)

	# get a command from the server
	def get_command(self):
		response = self.get()
		return json.loads(response.text)['command']

	# get a command from the server
	def get_zone(self):
		response = self.get('zone')
		return json.loads(response.text)

	# indicate that the drone is turning off by setting status to innactive
	def disconnect_from_server(self):
		self.flight_status = {
			'status': 'inactive',
			"timestamp": str(datetime.datetime.now())
		}
		post_status()

	# send and error message to the server if the drone failed to arm
	def send_err_message(self, error):
		self.flight_status = {
			'err': error,
			"timestamp": str(datetime.datetime.now())
		}
		post_status()

	def update_zone(self):
		r = self.get_zone()
		if r['latitude'] and r['longitude'] and r['altutide']:
			self.zone = r

	#################################################################################
	# PIXHAWK CONNECTIVITY/STATUS
	#################################################################################
	def disconnect_from_pixhawk(self):
		self.pixhawk.close()

	def get_state(self):
		self.flight_status = {
			# "type": self.type,
			# "name": self.name,
			"status": self.status,
			"timestamp": str(datetime.datetime.now()),
			"latitude": self.pixhawk.location.global_relative_frame.lat,
			"longitude": self.pixhawk.location.global_relative_frame.lon,
			"altitude": self.pixhawk.location.global_relative_frame.alt,
			"voltage": self.pixhawk.battery.voltage,
			"speed": self.pixhawk.groundspeed,
			"rssi": self.pixhawk.last_heartbeat, # use the time since the last heartbeat becase we don't have internet connectivity
		}
		return self.flight_status

	#################################################################################
	# MISSION PLANNING and FLIGHT CONTROL
	#################################################################################
	def land_and_disarm(self):
		self.pixhawk.mode = VehicleMode('LAND')
		while self.pixhawk.armed:
			print " Altitude: ", vehicle.location.global_relative_frame.alt
		print 'LANDED'
		self.status = 'landed'


	def go_to_location(self, lat, lon, alt, speed=5):
		target_location = LocationGlobalRelative(lat, lon, alt)
		self.pixhawk.simple_goto(target_location, speed)

	def arm_and_takeoff(self, target_alt=50):
		# Don't try to arm until autopilot is ready
		while not self.pixhawk.is_armable:
			print " Waiting for vehicle to initialise..."
			time.sleep(1)

		print "Arming motors"
		# Copter should arm in GUIDED mode
		self.pixhawk.mode	= VehicleMode("GUIDED")
		self.pixhawk.armed   = True

		# Confirm vehicle armed before attempting to take off
		while not pixhawk.armed:
			print " Waiting for arming..."
			time.sleep(1)

		print "Taking off!"
		self.pixhawk.simple_takeoff(target_alt) # Take off to target altitude

		# IZZY 2/5/17 - If we simply use a while loop with delay to wait for takeoff altitude, we
		# won't be able to respond to commands. This could be better implemented as a function that checks
		# if the drone has reached it's target location and blocks other functions until complete?

		# Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
		#  after Vehicle.simple_takeoff will execute immediately).
		while True:
			print " Altitude: ", self.pixhawk.location.global_relative_frame.alt
			#Break and return from function just below target altitude.
			if self.pixhawk.location.global_relative_frame.alt>=target_alt*0.95:
				print "Reached target altitude"
				break
			d.post_status() # keep posting status updates while climbing to altitude
			time.sleep(1)

	def mission_start(self):
		# perform some check to make sure the destination location is valid/not the one we're already at
		self.status = 'takingoff'
		self.arm_and_takeoff() # takeoff to the default altitude
		self.status = 'flying'
		d.post_status()	# post a status update to indicate forward flight
		self.go_to_location(self.zone['latitude'], self.zone['longitude'], self.zone['altitude'])

	def rtl(self):
		if self.status == 'flying':
			print 'WARNING: RTL.'
			self.pixhawk.mode = VehicleMode("RTL")
			self.status = 'rtl'
		else: print 'WARNING: cannot rtl while', d.status
		

if __name__ == "__main__":
	d = Drone()		# init the drone object
	select_input = ''
	idle_status_update_interval = 5
	iters_since_update = 0
	old_command = ''
	new_command = ''
	while(1):
		new_command = d.get_command()

		if new_command != old_command:
			old_command = new_command
			print 'Received', new_command, 'Current status:', d.status
			if new_command == 'rtl': d.rtl()
				
			elif new_command == 'pause':
				if d.status == 'flying':
					# TODO: how do I pause? set velocity to zero?
					# change mode to POS hold/LOITER? TBD
					d.status = 'paused'
				else: print 'WARNING: cannot pause while', d.status

			elif new_command == 'takeoff':
				if d.status == 'idle':
					# TODO: somehow calculate if the drone has enough battery left to perform the mission
					d.mission_start()
				else: print 'WARNING: cannot takeoff while', d.status

			elif new_command == 'idle':
				if d.status == 'landed':
					print 'idle'
					d.status = 'idle'
				else: print 'WARNING: cannot idle while', d.status
			elif new_command == 'updatezone':
				if d.pixhawk.armed:
					print 'ERROR: cannot update the target zone while', d.status
				else: d.get_zone()
			else:
				print 'ERROR: command', new_command, 'not recognized.'

			
		# post the status more slowly while idling
		if d.status == 'idle' and iters_since_update > idle_status_update_interval:
			d.post_status()
			iters_since_update = 0
		else: d.post_status()

		iters_since_update += 1
		time.sleep(1)

	
