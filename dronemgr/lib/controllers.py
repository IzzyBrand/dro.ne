from . util import DBFunc, Status

import random


""" Controller class for drone management logic """
class Controller:

    def __init__(self):
        self.db = DBFunc()
        Status.out("Connected to database")
        self.drone_uids = self.db.get_all("uid","drones")
        self.zone_uids = self.db.get_all("uid","zones")
        self.type_uids = self.db.get_all("uid","types")
        self.get = Get(self.db)
        self.set = Set(self.db)
        Status.out("Loaded information from database")

    # Run the following at each processing iteration (step)
    def step(self):
        for uid in self.drone_uids:
            name = self.get.general(uid)["name"]
            command = self.get.state(uid)["status"]
            Status.out("{}'s command: {}".format(name,command))
            # choose random command just to verify that setting values works
            self.set.status(uid,random.choice(["idle","takeoff","rtl","pause","landing"]))


""" Get information from database """
class Get:

    def __init__(self,db):
        self.db = db

    def position(self,uid):
        return {
            "latitude": self.db.get(uid,"latitude","drones"),
            "longitude": self.db.get(uid,"longitude","drones"),
            "altitude": self.db.get(uid,"altitude","drones"),
            "speed": self.db.get(uid,"speed","drones"),
            "timestamp": self.db.get(uid,"timestamp","drones")
        }

    def type(self,uid):
        type_uid = self.db.get(uid,"type","drones")
        return {
            "maxpayload": self.db.get(type_uid,"maxpayload","types"),
            "minvoltage": self.db.get(type_uid,"minvoltage","types"),
            "topspeed": self.db.get(type_uid,"topspeed","types"),
            "description": self.db.get(type_uid,"description","types")
        }

    def zone(self,uid):
        zone_uid = self.db.get(uid,"zone","drones")
        return {
            "latitude": self.db.get(zone_uid,"latitude","zones"),
            "longitude": self.db.get(zone_uid,"longitude","zones"),
            "altitude": self.db.get(zone_uid,"altitude","zones"),
            "description": self.db.get(zone_uid,"description","zones")
        }

    def state(self,uid):
        return {
            "command": self.db.get(uid,"command","drones"),
            "status": self.db.get(uid,"status","drones"),
            "error": self.db.get(uid,"error","drones"),
            "voltage": self.db.get(uid,"voltage","drones")
        }

    def general(self,uid):
        return {
            "name": self.db.get(uid,"name","drones"),
            "description": self.db.get(uid,"description","drones")
        }

    def all(self,uid):
        return {
            "position": self.position(),
            "type": self.type(),
            "zone": self.zone(),
            "state": self.state(),
            "general": self.general()
        }


""" Set information in database """
class Set:

    def __init__(self,db):
        self.db = db

    def status(self,uid,new_status):
        self.db.set(new_status,uid,"status","drones")