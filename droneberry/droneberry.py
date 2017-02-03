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
		# self.pixhawk = connect('/dev/cu.usbmodem1', baud = 115200) # for on mac via USB
		# self.pixhawk = connect('/dev/ttyS0', baud = 57600) # for on the raspberry PI via telem2

		# TODO: load from config
		self.api_url = "http://synapse/api"
		self.name = 'Gregg'
		self.uid = 'dUID'

		self.status = 'idle' # drone turns on in idle state

		#self.get_state() # flesh out the state

	#################################################################################
	# SERVER CONNECTIVITY
	#################################################################################

	# Post new drone state to server, print response
	def post_status(self):
		 payload = {
			 "uid": self.uid,
			 "auth": rt._encode("dronesrcool"),
			 "state": json.dumps(self.get_status_from_pixhawk())
		 }
		 response = requests.post(self.api_url, data=payload)
		 print response

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

	#################################################################################
	# PIXHAWK CONNECTIVITY/STATUS
	#################################################################################
	def disconnect_from_pixhawk(self):
		self.pixhawk.close()

	def get_state(self):
		self.flight_status = {
			# "type": self.type,
			# "name": self.name,
			"active": 1,
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


	def arm_and_takeoff(self, target_alt=20):
		# Don't try to arm until autopilot is ready
		while not vehicle.is_armable:
			print " Waiting for vehicle to initialise..."
			time.sleep(1)

		print "Arming motors"
		# Copter should arm in GUIDED mode
		self.vehicle.mode	= VehicleMode("GUIDED")
		self.vehicle.armed   = True

		# Confirm vehicle armed before attempting to take off
		while not vehicle.armed:
			print " Waiting for arming..."
			time.sleep(1)

		print "Taking off!"
		vehicle.simple_takeoff(target_alt) # Take off to target altitude

		# Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
		#  after Vehicle.simple_takeoff will execute immediately).
		while True:
			print " Altitude: ", vehicle.location.global_relative_frame.alt
			#Break and return from function just below target altitude.
			if vehicle.location.global_relative_frame.alt>=target_alt*0.95:
				print "Reached target altitude"
				break
			time.sleep(1)

	

if __name__ == "__main__":
	d = Drone()		# init the drone object
	select_input = ''
	while(1):
		select_input = ''
		select([], select_input,[],1)
		if select_input is not '':
			print 'Read ' + select_input

	
