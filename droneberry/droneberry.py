"""Connects to pixhawk and facilitates communication with backend"""

import requests
import json
import hashlib
import datetime
import time
from select import select
from dronekit import connect

# status - the one word description of the drone
# state  - the collection of information about the drone

class Drone:

	def start(self):
		self.pixhawk = connect('/dev/cu.usbmodem1', baud = 115200) # for on mac via USB
		self._log('Connected to pixhawk.')
		# self.pixhawk = connect('/dev/ttyS0', baud = 57600) # for on the raspberry PI via telem2
		config_loaded = self._load_config() # load info about the uid and auth
		online = True # TODO: verify internet connection
		return config_loaded and online

	def stop(self):
		self.disconnect_from_pixhawk()
		self.disconnect_from_server()
		self._log('Stopped.')
	#################################################################################
	# UTIL
	#################################################################################
	# load configuration from file
	def _load_config(self, file='droneconfig.json'):
		# TODO: error check all of this
		config_json = json.loads(open(file).read())
		self.api_url = config_json['api_url']
		self.name = config_json['name']
		self.uid = config_json['uid']
		self.auth = config_json['auth']
		self.status = config_json['startup_status']
		self._log('Successfully loaded config from ' + file)
		return True

	# logging abstracted so we can change where we are logging
	def _log(self, msg):
		print "[DEBUG]: {0}".format(msg)

	#################################################################################
	# SERVER CONNECTIVITY
	#################################################################################

	# QQ: are we ever going to have payloads with a different structure, or is this
	# all that we need to deal with from the drone?
	def post(self, state_json):
		payload = {
			 "uid": self.uid,
			 "auth": self.auth,
			 "state": json.dumps(state_json)
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

	# send state information from pixhawk
	def post_state(self):
		 payload_state = self.read_from_pixhawk()
		 post(payload_state)
	
	# send and error message to the server
	def post_err_message(self, error):
		d._log('SENDING ERROR: ' + error)
		payload_state = {
			'err': error,
			"timestamp": str(datetime.datetime.now())
		}
		post(payload_state)

	# indicate that the drone is turning off by setting status to innactive
	def disconnect_from_server(self):
		payload_state = {
			'status': 'inactive',
			"timestamp": str(datetime.datetime.now())
		}
		post(payload_state)

	# request a new zone from the server and update the local target zone
	def update_zone(self):
		r = self.get_zone()
		if r['latitude'] and r['longitude'] and r['altutide']:
			self.zone = r

	#################################################################################
	# PIXHAWK CONNECTIVITY/STATUS
	#################################################################################
	def disconnect_from_pixhawk(self):
		self.pixhawk.close()
		self._log('Disconnected from pixhawk.')

	def read_from_pixhawk(self):
		self.state = {
			"status": self.status,
			"timestamp": str(datetime.datetime.now()),
			"latitude": self.pixhawk.location.global_relative_frame.lat,
			"longitude": self.pixhawk.location.global_relative_frame.lon,
			"altitude": self.pixhawk.location.global_relative_frame.alt,
			"voltage": self.pixhawk.battery.voltage,
			"speed": self.pixhawk.groundspeed,
			"rssi": self.pixhawk.last_heartbeat # use the time since the last heartbeat becase we don't have internet connectivity
		}
		return self.state

	#################################################################################
	# MISSION PLANNING and FLIGHT CONTROL
	#################################################################################


#################################################################################
# MAIN
#################################################################################

if __name__ == "__main__":
	d = Drone()

	while(not d.start()):
		d.post_err_message("Failed to init.")

	# config delay and intervals
	loop_delay = 1
	get_interval = 1
	post_state_interval = 5 

	get_counter = 0
	post_state_counter = 0

	old_command = ''
	command = ''

	while(True):

		if get_counter <= 0:
			get_counter = get_interval
			command = d.get_command()

		if post_state_counter <= 0:
			post_state_counter = post_state_interval
			d.post_state()

		if command != old_command:
			


		get_counter -= loop_delay		# decrement the counters
		post_state_counter -= loop_delay

		time.sleep(loop_delay)

	d.stop()

	# def land_and_disarm(self):
	# 	self.pixhawk.mode = VehicleMode('LAND')
	# 	while self.pixhawk.armed:
	# 		print " Altitude: ", vehicle.location.global_relative_frame.alt
	# 	print 'LANDED'
	# 	self.status = 'landed'


	# def go_to_location(self, lat, lon, alt, speed=5):
	# 	target_location = LocationGlobalRelative(lat, lon, alt)
	# 	self.pixhawk.simple_goto(target_location, speed)

	# def arm_and_takeoff(self, target_alt=50):
	# 	# Don't try to arm until autopilot is ready
	# 	while not self.pixhawk.is_armable:
	# 		print " Waiting for vehicle to initialise..."
	# 		time.sleep(1)

	# 	print "Arming motors"
	# 	# Copter should arm in GUIDED mode
	# 	self.pixhawk.mode	= VehicleMode("GUIDED")
	# 	self.pixhawk.armed   = True

	# 	# Confirm vehicle armed before attempting to take off
	# 	while not pixhawk.armed:
	# 		print " Waiting for arming..."
	# 		time.sleep(1)

	# 	print "Taking off!"
	# 	self.pixhawk.simple_takeoff(target_alt) # Take off to target altitude

	# 	# IZZY 2/5/17 - If we simply use a while loop with delay to wait for takeoff altitude, we
	# 	# won't be able to respond to commands. This could be better implemented as a function that checks
	# 	# if the drone has reached it's target location and blocks other functions until complete?

	# 	# Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
	# 	#  after Vehicle.simple_takeoff will execute immediately).
	# 	while True:
	# 		print " Altitude: ", self.pixhawk.location.global_relative_frame.alt
	# 		#Break and return from function just below target altitude.
	# 		if self.pixhawk.location.global_relative_frame.alt>=target_alt*0.95:
	# 			print "Reached target altitude"
	# 			break
	# 		d.post_status() # keep posting status updates while climbing to altitude
	# 		time.sleep(1)

	# def mission_start(self):
	# 	# perform some check to make sure the destination location is valid/not the one we're already at
	# 	self.status = 'takingoff'
	# 	self.arm_and_takeoff() # takeoff to the default altitude
	# 	self.status = 'flying'
	# 	d.post_status()	# post a status update to indicate forward flight
	# 	self.go_to_location(self.zone['latitude'], self.zone['longitude'], self.zone['altitude'])

	# def rtl(self):
	# 	if self.status == 'flying':
	# 		print 'WARNING: RTL.'
	# 		self.pixhawk.mode = VehicleMode("RTL")
	# 		self.status = 'rtl'
	# 	else: print 'WARNING: cannot rtl while', d.status
		

# if __name__ == "__main__":
# 	d = Drone()		# init the drone object
# 	select_input = ''
# 	idle_status_update_interval = 5
# 	iters_since_update = 0
# 	old_command = ''
# 	new_command = ''
# 	while(1):
# 		new_command = d.get_command()

# 		if new_command != old_command:
# 			old_command = new_command
# 			print 'Received', new_command, 'Current status:', d.status
# 			if new_command == 'rtl': d.rtl()
				
# 			elif new_command == 'pause':
# 				if d.status == 'flying':
# 					# TODO: how do I pause? set velocity to zero?
# 					# change mode to POS hold/LOITER? TBD
# 					d.status = 'paused'
# 				else: print 'WARNING: cannot pause while', d.status

# 			elif new_command == 'takeoff':
# 				if d.status == 'idle':
# 					# TODO: somehow calculate if the drone has enough battery left to perform the mission
# 					d.mission_start()
# 				else: print 'WARNING: cannot takeoff while', d.status

# 			elif new_command == 'idle':
# 				if d.status == 'landed':
# 					print 'idle'
# 					d.status = 'idle'
# 				else: print 'WARNING: cannot idle while', d.status
# 			elif new_command == 'updatezone':
# 				if d.pixhawk.armed:
# 					print 'ERROR: cannot update the target zone while', d.status
# 				else: d.get_zone()
# 			else:
# 				print 'ERROR: command', new_command, 'not recognized.'

			
# 		# post the status more slowly while idling
# 		if d.status == 'idle' and iters_since_update > idle_status_update_interval:
# 			d.post_status()
# 			iters_since_update = 0
# 		else: d.post_status()

# 		iters_since_update += 1
# 		time.sleep(1)

	
