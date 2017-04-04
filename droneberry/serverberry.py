import requests
import json
import hashlib
import datetime
import sys

class ServerInterface:
	# set the configuration
	def config(self, uid, auth, api_url, name):
		self.uid = uid
		self.auth = auth
		self.api_url = api_url
		self.name = name

	def post(self, state_json):
		# TODO: verify
		payload = {
			 "uid": self.uid,
			 "auth": self.auth,
			 "state": json.dumps(state_json)
		 }
		response = requests.post(self.api_url, data=payload)
		if response.status_code - 200 < 10:
			return response.text
		else: 
			print '[POST ERROR]: got status code', str(response.status_code)
			return None

	def get(self, subset=None):
		if subset: payload = "uid={}&subset={}".format(self.uid, subset)
		else: payload = "uid={}".format(self.uid)
		response = requests.get(self.api_url, params=payload)
		if response.status_code - 200 < 10:
			return response.text
		else: 
			print '[GET ERROR]: got status code', str(response.status_code)
			return None


	# get a command from the server
	def get_command(self):
		r = self.get()
		return json.loads(r)['command']

	# get the job json from the server (this has all the info about the mission)
	def get_job(self):
		r = self.get('job')
		return json.loads(r)
	
	# send and error message to the server
	def post_err_message(self, error):
		payload_state = {
			'err': error,
			"timestamp": str(datetime.datetime.now())
		}
		self.post(payload_state)

	# indicate that the drone is turning off by setting status to innactive
	def disconnect(self):
		payload_state = {
			'status': 'inactive',
			"timestamp": str(datetime.datetime.now())
		}
		self.post(payload_state)

