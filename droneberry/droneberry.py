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
# from gripper import Gripper
# from gpiozero import Button
from missionHandler import upload
from serverberry import ServerInterface
from dronekit import connect, VehicleMode
from pymavlink import mavutil
import sys
import os



class Drone:
	_COMMAND_SET_MISSION 	= 'updatezone'
	_COMMAND_START			= 'start'
	_COMMAND_TAKEOFF 		= 'takeoff'
	_COMMAND_LAND 			= 'land'
	_COMMAND_PAUSE			= 'pause'
	_COMMAND_RTL 			= 'rtl'
	_COMMAND_SHUTDOWN		= 'shutdown'

	def start(self):
		self.server = ServerInterface()
		self.pixhawk = connect('/dev/cu.usbmodem1', baud = 115200, wait_ready=True) # for on mac via USB
		# self.pixhawk = connect('/dev/tty.usbserial-DA00BL49', baud = 57600)
		# self.pixhawk.wait_ready(timeout=60)
		# self.pixhawk = connect('/dev/ttyS0', baud = 57600, wait_ready=True) # for on the raspberry PI via telem2
		self._log('Connected to pixhawk.')
		self._prev_command = ''
		self._arming_window_start = 0
		self.current_action = 'idle'
		config_loaded = self._load_config() # load info about the uid and auth
		online = True # TODO: verify internet connection
		# self.gripper = Gripper(18) # set up the gripper
		# self.button = Button(2)	   # set up the button
		# self.button.when_pressed   = self.gripper.open
		# self.button.when_released  = self.gripper.close

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
		# if self.state['voltage'] < voltage_emergency_threshold:
			# RTL

		# SEND STATE UPDATE
		self.server.post(self.state)

		# REQUEST COMMAND
		received_command = self.server.get_command()

		# ACT ON NEW COMMAND COMMAND
		if received_command != self._prev_command:
			self._log('received command - ' + received_command)

			if received_command == self._COMMAND_START:
				self.set_action('prearm')
			elif received_command == self._COMMAND_TAKEOFF:
				self.set_action('arm')
			elif received_command == self._COMMAND_LAND:
				if self.current_action == 'wait_land':
					self.pixhawk.commands.next += 1 # advance to the landing waypoint
					self.current_action = 'landing'
				else: self._log('WARNING - Cannot land while ' + self.current_action)
			elif received_command == self._COMMAND_RTL:
				self.set_action('start_rtl')
			elif received_command == self._COMMAND_PAUSE:
				self.set_action('pause')
			elif received_command == self._COMMAND_SET_MISSION:
				if not self.pixhawk.armed:
					wp_file = self.server.get_job()['wp_file']
					wp_to_load = self.wp_path + '/' + wp_file + '.txt'
					# TODO: figure out how to error check command upload
					upload(self.pixhawk, self.wp_path + '/' + wp_file + '.txt')
					self.pixhawk.commands.download()
					self.current_action = 'idle'

			elif received_command == self._COMMAND_SHUTDOWN:
				if not self.pixhawk.armed:
					self.stop()
					# os.system("sudo shutdown -h now")

			self._prev_command = received_command


		# ACT ON ONGOING ACTION
		# the self.current_action allows us to have ongoing instructions
		if self.current_action == 'prearm':
			self.pixhawk.mode = VehicleMode('GUIDED') # we arm and takeoff in guided mode
			self.pixhawk.commands.wait_ready() # we can't fly until we have commands list
			self._arming_window_start = time.time()
			self.current_action = 'wait_arm'

		elif self.current_action == 'wait_arm' and time.time() - self._arming_window_start > 60:
			self._log('TIMEOUT - revert to idle')
			self.current_action = 'idle'

		elif self.current_action == 'arm':
			self.pixhawk.armed = True
			self.current_action = 'takeoff'

		elif self.current_action == 'takeoff' \
			and self.pixhawk.armed: # we need to verify that the pixhawk is armed
			self.pixhawk.simple_takeoff(20)
			self.current_action = 'mission_start'

		elif self.current_action == 'mission_start':
			self.pixhawk.commands.next = 0	# start from the first waypoint
			self.pixhawk.mode = VehicleMode('AUTO')
			self.current_action = 'flying'

		elif self.current_action == 'flying':
			next_cmd = self.pixhawk.commands.next
			# TODO - Determine if this should be mavutil.mavlink.MAV_CMD_NAV_LAND instead?
			if self.pixhawk.commands[next_cmd].command == mavutil.mavlink.MAV_CMD_NAV_LOITER_UNLIM:
				# we've reached the loiter waypoint
				self.current_action = 'wait_land'

		elif self.current_action == 'landing' and not self.pixhawk.armed:
			# we were landing and now we're disarmed, so we must have landed
			self.gripper.open()
			self.current_action = 'idle'

		elif self.current_action == 'disarm': 
			self._log('disarm')
			self.pixhawk.armed = False
			if not self.pixhawk.armed: self.current_action = 'idle'
			else:	self._log('DISARM FAILED')

		elif self.current_action == 'pause':
			self.pixhawk.mode = VehicleMode('LOITER')
			self._log('LOITER')
			self.current_action = 'loiter'

		elif self.current_action == 'start_rtl':
			self.pixhawk.mode = VehicleMode('RTL')
			self._log('RTL')
			self.current_action = 'rtl'


	#################################################################################
	# STATE FLOW LOGIC
	#################################################################################
	def set_action(self, new_action):
		if new_action == 'start_rtl':
			# disarm if we haven't taken off yet
			if self.current_action == 'prearm' \
			or self.current_action == 'wait_arm' \
			or self.current_action == 'arm' \
			or self.current_action == 'takeoff' \
			or self.current_action == 'disarm':
				self.current_action = 'disarm'

			else: self.current_action = 'start_rtl'

		elif new_action == 'pause':
			# disarm if we haven't taken off yet
			if self.current_action == 'prearm' \
			or self.current_action == 'wait_arm' \
			or self.current_action == 'arm' \
			or self.current_action == 'takeoff' \
			or self.current_action == 'disarm':
				self.current_action = 'disarm'

			# pause if we are flying
			elif self.current_action == 'flying' \
			or self.current_action == 'mission_start' \
			or self.current_action == 'landing' \
			or self.current_action == 'rtl':
				self.current_action = 'pause'

			else: self._log('WARNING - Cannot pause while ' + self.current_action)

		elif new_action == 'prearm':
			if self.current_action == 'idle': self.current_action = 'prearm'
			else: self._log('WARNING - Cannot start while ' + self.current_action)

		elif new_action == 'arm':
			if self.current_action == 'wait_arm': self.current_action = 'arm'
			else: self._log('WARNING - Cannot arm and takeoff while ' + self.current_action)

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
		self.status = config_json['startup_status']
		self.wp_path = config_json['wp_path']
		self._log('Successfully loaded config from ' + file)
		return True

	# logging abstracted so we can change where we are logging
	def _log(self, msg):
		print "[DEBUG]: {0}".format(msg)

	#################################################################################
	# PIXHAWK CONNECTIVITY
	#################################################################################
	def _read_from_pixhawk(self):
		# TODO: add timeout on this?
		self.state = {
			"status": self.current_action,
			"timestamp": str(datetime.datetime.now()),
			"latitude": self.pixhawk.location.global_relative_frame.lat,
			"longitude": self.pixhawk.location.global_relative_frame.lon,
			"altitude": self.pixhawk.location.global_relative_frame.alt,
			"voltage": self.pixhawk.battery.voltage,
			"speed": self.pixhawk.groundspeed,
			"rssi": self.pixhawk.last_heartbeat # use the time since the last heartbeat becase we don't have internet connectivity
		}
		return self.state


if __name__ == "__main__":
    d = Drone()
    d.start()
    try:
        while True:
        	d.step()
        	time.sleep(1)
    except KeyboardInterrupt:
        d.stop()
