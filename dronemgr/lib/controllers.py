from . util import DBFunc, Status

import random


""" Controller class for drone management logic """
class Controller:

    def __init__(self):
        self.db = DBFunc()
        Status.out("Connected to database")
        # NOTE: by preloading the drones, we don't allow the manager to handle
        # dynamically adding a new drone to the database
        self.drone_uids = self.db.get_all("uid","drones")
        self.get = Get(self.db)
        self.set = Set(self.db)
        # a list of dicts to store each drone
        self.drones = map(lambda uid: {
            'uid':uid, 
            'name':self.get.general(uid)['name']}, self.drone_uids)
        Status.out("Loaded information from database")

    # Run the following at each processing iteration (step)
    def step(self):
        exists_idle_drone = False

        # update the status of each drone
        for d in self.drones: 
            s = self.get.state(d['uid']) # TODO: do we need to error check this?
            d['status'] = s['status']
            d['voltage'] = s['voltage']
            exists_idle_drone = exists_idle_drone or (d['status'] == 'idle')

        # refresh the orders list if there is an idle drone to handle a new task
        if exists_idle_drone: self.orders = map(lambda order_uid: 
            self.get.order(order_uid), self.db.get_all('uid','orders'))

        for d in self.drones:
            if d['status'] == 'idle':
                order_uid = self.get_oldest_doable_order(d['uid'])
                # if the drone can't handle the shortest order in the list or if there are no 
                # orders queued, then we may as well change the battery on the drone
                if order_uid is None:
                    # NOTE: we need to decide how exactly we want to handle this
                    d.set.command(d['uid'], 'change_battery')
                else:
                    task_uid = self.create_task_from_order(d['uid'], order_uid)
                    d.set.command(d['uid'], 'updatemission')
                    # TODO: how do we tell the hub workers what to pack onto which drone

            elif d['status'] == 'wait_arm':
            elif d['status'] == 'wait_land':


    # goes through the order list and retrieves the uid which corresponds to the
    # order which has waited longest which the drone could handle right now
    def get_oldest_doable_order(self, drone):
        # for the purposes of a single site demo, we only need a lower voltage
        # threshold. The logic here will need to be updated when we introduce multiple
        # sites. 
        if drone['voltage'] < 15.5:
            Status.out("Drone {} has insufficient voltage ({}v) to complete a job".
                format(drone['name'], drone['voltage']))
            return None
        else:
            oldest_incomplete_order = None
            for o in orders:
                # TODO: I've coded this assuming and order get's assigned a drone
                # when it get's turned into a task. is this the way we want to
                # represent that an order is being handled?
                if o['drone_uid'] == '' and (oldest_incomplete_order is None \
                or o['timestamp'] < oldest_incomplete_order['timestamp']):
                        oldest_incomplete_order = o

            if oldest_incomplete_order is None: return None
            else: return oldest_incomplete_order['uid']


    # creates a new task from the given order_uid and assigns it to
    # the given drone_uid. the uid of the new task is returned
    def create_task_from_order(self, drone_uid, order_uid):
        # TODO: implement this once db structure is clarified
        return 'task_uid'


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

    def job(self,uid):
        job_uid = self.db.get(uid,"job","drones")
        return {
            "uid": self.db.get(job_uid,"uid","jobs"),
            "username": self.db.get(job_uid,"username","jobs"),
            "flavor": self.db.get(job_uid,"flavor","jobs"),
            "destination": self.db.get(job_uid,"destination","jobs"),
            "timestamp": self.db.get(job_uid,"timestamp","jobs")
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

    def order(self,uid):
        # TODO: this will need to be updated once we clarify exactly what the orders
        # db structure is. do we have a field for eta? for which drone? for completed?
        return {
            'uid': uid,
            'destination': self.db.get(uid, 'destination', 'orders'),
            'timestamp': self.db.get(uid, 'timestamp', 'orders')
            'drone_uid': self.db.get(uid, 'drone_uid', 'orders')
        }


""" Set information in database """
class Set:

    def __init__(self,db):
        self.db = db

    def status(self,uid,new_status):
        self.db.set(new_status,uid,"status","drones")

    def job(self,uid,new_job=None):
        self.db.set(new_job,uid,"job","drones")

    def command(self,uid, new_command):
        self.db.set(new_command,uid,"command","drones")