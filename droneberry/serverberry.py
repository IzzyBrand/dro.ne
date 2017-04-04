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
		try:
		    response = requests.post(self.api_url, data=payload)
		except requests.exceptions.RequestException as e:  # This is the correct syntax
		    print e
		    sys.exit(1)
		return response

	def get(self, subset=None):
		if subset: payload = "uid={}&subset={}".format(self.uid, subset)
		else: payload = "uid={}".format(self.uid)
		return requests.get(self.api_url, params=payload)


	# get a command from the server
	def get_command(self):
		response = self.get()
		return json.loads(response.text)['command']

	# get the job json from the server (this has all the info about the mission)
	def get_job(self):
		response = self.get('job')
		return json.loads(response.text)
	
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

