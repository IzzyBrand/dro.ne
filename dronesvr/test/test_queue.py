from requests import Request, Session
import json, datetime

def get_job():
    return {
        "uid": "J30jjfs",
        "pickupzone": "Z123",
        "dropoffzone": "Z456",
        "sender": "ben",
        "receiver": "izzy",
        "desired_pickup_time": "now",
        "timestamp": str(datetime.datetime.now())
    }


url = 'http://localhost/api'
data = {
    "username": "ben",
    "password": "",  # Removed password
    "job": json.dumps(get_job())
}

s = Session()
req = Request("PUT",url,data=data)

preparedReq = s.prepare_request(req)

resp = s.send(preparedReq)

print resp.status_code, json.loads(resp.text)