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
 - notice when command goes unserved and timeout appropriately


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
from dronekit import connect, VehicleMode, APIException
from pymavlink import mavutil
import sys
import os
# TODO:
"""
 - set departure and arrival times in task so our records are straight
"""


class Drone:
        _COMMAND_ADVANCE_MISSION        = 'advancemission'
	_COMMAND_SET_MISSION 	        = 'updatemission'
	_COMMAND_START			= 'start'
	_COMMAND_TAKEOFF 		= 'takeoff'
	_COMMAND_LAND 			= 'land'
	_COMMAND_PAUSE			= 'pause'
	_COMMAND_RTL 			= 'rtl'
	_COMMAND_SHUTDOWN		= 'shutdown'

	def start(self):
		self.server = ServerInterface()
		self.pixhawk = connect('/dev/ttyACM0', baud = 115200, wait_ready=True) 	# for on mac via USB
		# self.pixhawk = connect('/dev/ttyS0', baud = 57600, wait_ready=True) 			# for on the raspberry PI via telem2
		# # self.pixhawk = connect('/dev/tty.usbserial-DA00BL49', baud = 57600)			# telem radio on mac
		# # self.pixhawk = connect('/dev/tty.SLAB_USBtoUART', baud = 57600)				# telem radio on mac
		#self.pixhawk.wait_ready(timeout=60)
		self._log('Connected to pixhawk.')
		self.pixhawk.commands.download()
		self._prev_pixhawk_mode = ''
		self._prev_command = ''
		self._arming_window_start = 0
		self._server_connect_timer = time.time()
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
		# UPDATE PIXHAWK INFORMATION
		self._read_from_pixhawk()
		self.print_mode_change()
		# if self.state['voltage'] < voltage_emergency_threshold:
			# RTL

		# SEND STATE UPDATE
		self.server.post_state(self.state)

		# REQUEST COMMAND
		received_command = self.server.get_command()
		# force an RTL if we haven't received a new command in more than 30 seconds
		if received_command != None: self._server_connect_timer = time.time()
		elif time.time() - self._server_connect_timer > 30: received_command = self._COMMAND_RTL

		# ACT ON NEW COMMAND COMMAND
		if received_command != self._prev_command:
			self._log('received command - ' + str(received_command))

			if received_command == self._COMMAND_START:
				self.flow_action('prearm')
			elif received_command == self._COMMAND_TAKEOFF:
				self.flow_action('arm')
			elif received_command == self._COMMAND_LAND:
				if self.current_action == 'wait_land':
					self.pixhawk.commands.next += 1 # advance to the landing waypoint
					self.set_action('landing')
				else: self._log('WARNING - Cannot land while ' + self.current_action)
			elif received_command == self._COMMAND_RTL:
				self.flow_action('start_rtl')
			elif received_command == self._COMMAND_PAUSE:
				self.flow_action('pause')
			elif received_command == self._COMMAND_SET_MISSION:
				if not self.pixhawk.armed:
					wp_file = self.server.get_mission()
					if wp_file != None:
						wp_to_load = self.wp_path + '/' + wp_file + '.txt'
						# TODO: figure out how to error check command upload
						mission_to_upload = self.pixhawk, self.wp_path + '/' + wp_file + '.txt'
						print 'Preparing to upload', mission_to_upload
						upload(self.pixhawk, self.wp_path + '/' + wp_file + '.txt')
						self.pixhawk.commands.download()
						self.server.post_mission(wp_file)
						self.set_action('idle')
					else: print 'ERROR: Failed to get wp file name'

                        elif received_command == self._COMMAND_ADVANCE_MISSION:
                                if self.current_action == 'idle':
                                        self.set_action('taskme')
                                else: self._log('WARNING - Cannot advance task while ' + self.current_action)
			elif received_command == self._COMMAND_SHUTDOWN:
				if not self.pixhawk.armed:
					self.stop()
					# os.system("sudo shutdown -h now")

			self._prev_command = received_command


		# ACT ON ONGOING ACTION
		# the self.current_action allows us to have ongoing instructions
		if self.current_action == 'prearm':
			self.pixhawk.mode = VehicleMode('GUIDED') # we arm and takeoff in guided mode
			try:
				self.pixhawk.commands.wait_ready() # we can't fly until we have commands list
				self._arming_window_start = time.time()
				self.set_action('wait_arm')
			except APIException:
				print 'commands still downloading.'
				self.set_action('idle')

		elif self.current_action == 'wait_arm' and time.time() - self._arming_window_start > 60:
			self._log('TIMEOUT - revert to idle')
			self.set_action('idle')

		elif self.current_action == 'arm':
			self.pixhawk.armed = True
			self._log('arm')
			self.set_action('takeoff')

		elif self.current_action == 'takeoff' \
			and self.pixhawk.armed: # we need to verify that the pixhawk is armed
			self.pixhawk.simple_takeoff(20)
			self.set_action('mission_start')

		elif self.current_action == 'mission_start':
			self.pixhawk.commands.next = 0	# start from the first waypoint
			self.pixhawk.mode = VehicleMode('AUTO')
			self.set_action('flying')

		elif self.current_action == 'flying':
			next_cmd = self.pixhawk.commands.next
			print next_cmd, self.pixhawk.commands[next_cmd].command
			# TODO - Determine if this should be mavutil.mavlink.MAV_CMD_NAV_LAND instead?
			if self.pixhawk.commands[next_cmd].command == mavutil.mavlink.MAV_CMD_NAV_LOITER_UNLIM:
				# we've reached the loiter waypoint
				self.set_action('wait_land')

		# if there is a consectutive land followed by a takeoff waypoint, then we actuate the 
		# gripper on the takeoff waypoint so we release the box just before we leave the ground.
		# if there is no takeoff waypoint and the pixhawk disarms, open the gripper anyway just to
		# be safe
		elif self.current_action == 'landing':
			if not self.pixhawk.armed:
				self.gripper.open()
				self.set_action('disarm')
			elif self.pixhawk.commands[next_cmd].command == mavutil.mavlink.MAV_CMD_NAV_TAKEOFF:
				self.gripper.open()
				self.set_action('flying')

		elif self.current_action == 'disarm': 
			self._log('disarm')
			self.pixhawk.armed = False
			if not self.pixhawk.armed: self.set_action('idle')
			else:	self._log('DISARM FAILED')

		elif self.current_action == 'pause':
			self.pixhawk.mode = VehicleMode('LOITER')
			self.set_action('loiter')

		elif self.current_action == 'start_rtl':
			self.pixhawk.mode = VehicleMode('RTL')
			self.set_action('rtl')

		elif (self.current_action == 'rtl' or self.current_action == 'loiter') \
		and not self.pixhawk.armed:
			self._log('Detected disarm while ' + self.current_action + '. Changing to idle.')
			self.set_action('idle')

	#################################################################################
	# STATE FLOW LOGIC
	#################################################################################
	def set_action(self, new_action):
		self._log('[ACTION] - ' + new_action)
		self.current_action = new_action

	def flow_action(self, new_action):
		if new_action == 'start_rtl':
			# disarm if we haven't taken off yet
			if self.current_action == 'prearm' \
			or self.current_action == 'wait_arm' \
			or self.current_action == 'arm' \
			or self.current_action == 'takeoff' \
			or self.current_action == 'disarm':
				self.set_action('disarm')

			else: self.set_action('start_rtl')

		elif new_action == 'pause':
			# disarm if we haven't taken off yet
			if self.current_action == 'prearm' \
			or self.current_action == 'wait_arm' \
			or self.current_action == 'arm' \
			or self.current_action == 'takeoff' \
			or self.current_action == 'disarm':
				self.set_action('disarm')

			# pause if we are flying
			elif self.current_action == 'flying' \
			or self.current_action == 'mission_start' \
			or self.current_action == 'landing' \
			or self.current_action == 'rtl':
				self.set_action('pause')

			else: self._log('WARNING - Cannot pause while ' + self.current_action)

		elif new_action == 'prearm':
			if self.current_action == 'idle': self.set_action('prearm')
			else: self._log('WARNING - Cannot start while ' + self.current_action)

		elif new_action == 'arm':
			if self.current_action == 'wait_arm': self.set_action('arm')
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

	def print_mode_change(self):
		if self.pixhawk.mode.name != self._prev_pixhawk_mode:
			print 'MODE CHANGED TO', self.pixhawk.mode.name
			self._prev_pixhawk_mode = self.pixhawk.mode.name

if __name__ == "__main__":
    d = Drone()
    d.start()
    try:
        while True:
        	d.step()
        	time.sleep(1)
    except KeyboardInterrupt:
        d.stop()
