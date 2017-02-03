""" Test DroneServer API by simulating drones"""

import requests
import json
import hashlib
import random
import datetime
import time


class RequestTester:

    def __init__(self):
        self.API = "http://localhost/api"
        self.zoneUID = 'ZUID'

    # Generate fake coordinates, altitude, battery voltage
    def _gen_coords(self):
        s1 = str(random.random() * 100)
        s2 = str(random.random() * 100)
        return s1[:16], s2[:16]
    def _gen_altitude(self):
        s = str(random.random() * 50)
        return s[:16]
    def _gen_voltage(self):
        s = str(random.random() * 16.8)
        return s[:8]
    def _gen_speed(self):
        s = str(random.random() * 8)
        return s[:8]
    def _gen_rssi(self):
        s = str(random.random() * 100)
        return s[:8]

    # Generate fake drone state to pass to server
    def _gen_state(self, uid):
        latitude, longitude = self._gen_coords()
        d = {
            "uid": uid,
            "timestamp": str(datetime.datetime.now()),
            "name": random.choice(["Gregg","Jimmy","Sam","Maria","Lauren","Annie","Paul"]),
            "latitude": latitude,
            "longitude": longitude,
            "altitude": self._gen_altitude(),
            "voltage": self._gen_voltage(),
            "speed": self._gen_speed(),
            "rssi": self._gen_rssi(),
            "destination": random.choice(["zUID","ZABC","Z201jt"])
        }
        return d

    # Generate md5 hex of string
    def _encode(self, string):
        m = hashlib.md5()
        m.update(string)
        return m.hexdigest()

    # Post new drone state to server, print response
    def post(self, uid, auth, valid=True):
        auth = auth if valid else "123abcTHISwontWORK"
        payload = {
            "uid": uid,
            "auth": auth,
            "state": json.dumps(self._gen_state(uid))
        }
        r = requests.post(self.API, data=payload)
        return r

    # Get current drone state from server, print response
    def get(self, uid, valid=True):
        uid = uid if valid else "fakeUID"
        payload = "uid={}".format(uid)
        r = requests.get(self.API, params=payload)
        return r

    def get_all(self):
        return requests.get(self.API)


if __name__ == "__main__":

    update_delay = 1

    rt = RequestTester()
    uid_list = rt.get_all()
    uid_list = json.loads(uid_list.text)
    auth = rt._encode("dronesrcool")

    # Simulate all drones sending POSTing to server
    while True:
        for uid in uid_list["uids"]:
            r = rt.post(uid, auth)
            print "POST ({}) returned status {}".format(uid,r.status_code)
        time.sleep(update_delay)

    # print "==============================="
    # print "Bad GET request (invalid UID):"
    # r = rt.get(False)
    # print "Status code:", r.status_code
    # print "Response:", r.text

    # print "==============================="
    # print "GET request:"
    # r = rt.get()
    # print "Status code:", r.status_code
    # print "Response:", r.text

    # print "==============================="
    # print "Bad POST request (invalid AUTH):"
    # r = rt.post(False)
    # print "Status code:", r.status_code
    # print "Response:", r.text

    # print "==============================="
    # print "POST request:"
    # r = rt.post()
    # print "Status code:", r.status_code
    # print "Response:", json.loads(r.text)

    # print "==============================="
    # print "GET request:"
    # r = rt.get()
    # print "Status code:", r.status_code
    # print "Response:", r.text

    # print "==============================="