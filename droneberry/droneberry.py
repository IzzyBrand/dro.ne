"""
Izzy Brand and Ben Shanahan
3/10/17

Handles drone-side interactions with the flight controller and the server.
"""

"""
FUNCTIONALITY BRAINSTORM
 - constantly sending status updates
 - constantly requesting commands
 - responding to commands
 	- missions
 	- flying
 - monitor battery
 - log activity

 FEATURES THAT WE PROB NEED
 - timeouts on most functions to keep loop update high
"""

import json
import datetime
import time
from missionHandler import upload_and_verify
from serverberry import ServerInterface
from dronekit import connect, VehicleMode


class Drone:

	self._COMMAND_SET_MISSION 	= 'updatezone'
	self._COMMAND_TAKEOFF 		= 'takeoff'
	self._COMMAND_RTL 			= 'rtl'

	def start(self):
		self.server = ServerInterface()
		self.pixhawk = connect('/dev/cu.usbmodem1', baud = 115200) # for on mac via USB
		self._log('Connected to pixhawk.')
		self._prev_command = ''
		# self.pixhawk = connect('/dev/ttyS0', baud = 57600) # for on the raspberry PI via telem2
		config_loaded = self._load_config() # load info about the uid and auth
		online = True # TODO: verify internet connection
		return config_loaded and online

	def stop(self):
		self.pixhawk.close()
		self.server.disconnect()
		self._log('Stopped.')

	#################################################################################
	# STEP
	#################################################################################
	def step(self):
		# CHECK BATTERY VOLTAGE
		self._read_from_pixhawk()
		if self.status['voltage'] < voltage_emergency_threshold:
			# RTL

		# SEND STATE UPDATE
		self.server.post(self.state)

		# REQUEST COMMAND
		received_command = self.server.get_command()

		# ACT ON COMMAND
		if received_command != self._prev_command:
			self._log('NEW COMMAND - ' + received_command)

			if received_command == self._COMMAND_RTL:
				self.pixhawk.mode = VehicleMode('RTL')

			elif received_command == self._COMMAND_SET_MISSION:

			elif received_command == self._COMMAND_TAKEOFF:
				self.pixhawk.mode = VehicleMode('AUTO')

	#################################################################################
	# UTIL
	#################################################################################
	# load configuration from file
	def _load_config(self, file='droneconfig.json'):
		# TODO: error check all of this
		config_json = json.loads(open(file).read())
		self.server.config(
			config_json['uid'], 
			config_json['auth'], 
			config_json['api_url'], 
			config_json['name'])
		# self.api_url = config_json['api_url']
		# self.name = config_json['name']
		# self.uid = config_json['uid']
		# self.auth = config_json['auth']
		self.status = config_json['startup_status']
		self._log('Successfully loaded config from ' + file)
		return True

	# logging abstracted so we can change where we are logging
	def _log(self, msg):
		print "[DEBUG]: {0}".format(msg)

	# request a new zone from the server and update the local target zone
	def _update_zone(self):
		r = self.server.get_zone()
		if r['latitude'] and r['longitude'] and r['altutide']:
			self.zone = r

	#################################################################################
	# PIXHAWK CONNECTIVITY
	#################################################################################
	def _read_from_pixhawk(self):
		# TODO: add timeout on this?
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


