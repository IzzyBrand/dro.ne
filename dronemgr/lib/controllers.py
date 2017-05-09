from . util import DBFunc, Status, Get, Set
from dateutil import parser
from datetime import datetime
import random


""" Controller class for drone management logic """
class Controller:

    def __init__(self):
        self.db = DBFunc()
        Status.out("Connected to database")
        # NOTE: by preloading the drones, we don't allow the manager to handle
        # dynamically adding a new drone to the database
        self.drone_uids = self.get.list("uid","drones")
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

        # update the state of each drone
        for d in self.drones: 
            s = self.get.state(d['uid']) # TODO: do we need to error check this?
            d['status'] = s['status']
            d['voltage'] = s['voltage']
            exists_idle_drone = exists_idle_drone or (d['status'] == 'idle')

        # refresh the orders list if there is an idle drone to handle a new task
        if exists_idle_drone: self.orders = map(lambda order_uid: 
            self.get.order(order_uid), self.get.list('uid','orders', completed='0'))

        for d in self.drones:
            if d['status'] == 'idle':
                order = self.get_oldest_doable_order(d['uid'])
                if order is None:
                    # NOTE: if the drone can't handle the shortest order in the list or if there are no 
                    # orders queued, then we may as well change the battery on the drone
                    self.set.status(d['uid'], 'changebattery')
                else:
                    task_uid = self.create_task_from_order(d['uid'], order)
                    if task_uid:
                        self.set.task(d['uid'], task_uid)           # update the drone's task
                        self.set.command(d['uid'], 'updatemission') # tell the drone to update its wp file
                        self.set.status('wait_start')               # don't let the drone get overwritten
                        # BEN TODO: we could set a frontend command flag "loadorder" or something
                        # and then the front-end knows to grab the items for the current drone's order.
                    else:
                        Status.out("ERROR - Failed to create a task from order {} for drone {}.".
                            format(order['uid'], drone['name']))


    ###################################################
    ###               HELPER FUNCTIONS              ###
    ###################################################

    # goes through the order list and retrieves the uid which corresponds to the
    # order which has waited longest which the drone could handle right now
    def get_oldest_doable_order(self, drone, orders):
        if drone['voltage'] < 14.8: # TODO: change this check to take into account the drone's type
            Status.out("Drone {} has insufficient voltage ({}v) to complete a job".
                format(drone['name'], drone['voltage']))
            return None
        else:
            oldest_incomplete_order = None
            for order in orders:
                if self.drone_can_handle_order(drone, order) and (oldest_incomplete_order is None \
                or order['timestamp'] < oldest_incomplete_order['timestamp']):
                        oldest_incomplete_order = order

            if oldest_incomplete_order is None: return None
            else: return oldest_incomplete_order

    # takes a drone and an order and returns true if the drone would be capable
    # of carrying that order
    # TODO: in the future, we can reference a drone's payload/range/power and the order's
    # weight/distance to assess if the given drone can handle the given order.
    # TODO: if we do want to cluster multiple orders into a task, then we need to generate
    # candidate tasks to check as opposed to just checking the individual orders
    def drone_can_handle_order(self, drone, order):
        return drone['voltage'] > 15.5

    # creates a new task from the given order and assigns it to
    # the given drone_uid. the uid of the new task is returned
    def create_task_from_order(self, drone_uid, order):
        mission = self.get_mission_from_destination(order['destination'])
        new_task = {
            'drone': drone_uid,
            'orders': order['uid'], # NOTE: we may change this to be a list of orders
            'mission': mission
        }
        return self.db.add_task(new_task)

    # TODO: takes a destination (or hopefully a sequence of destinations at some point) and returns 
    # a wp filename (or hopefully just a series of waypoints at some point)
    def get_mission_from_destination(self, destination):
        # NOTE: I know this looks silly. For the first demo all missions are out and back
        # and the names of the wp files are the same as the destination
        if destination   == 'ruthsimmons':  return 'ruthsimmons'
        elif desintation == 'maingreen':    return 'maingreen'
        elif destination == 'quietgreen'    return 'quietgreen'


