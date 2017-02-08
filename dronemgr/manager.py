from lib.util import Status, DBFunc

import os
import time

"""
Manager (just a state machine) that delegates and manages deployed
drones, etc.

The main focus of this manager is to coordinate all of the
management subfunctions as well as make database calls.
"""
class Manager:

    def __init__(self):
        self.db = DBFunc()
        self.running = True
        Status.out("Connected to database")

    def start(self):
        Status.out("Manager started")
        self.block()

    def stop(self):
        Status.out("Stopping manager")
        self.running = False

    def block(self):
        while self.running:
            self.db.set_uid("dUID")
            latitude = self.db.get_drone("latitude")
            longitude = self.db.get_drone("longitude")
            altitude = self.db.get_drone("altitude")
            Status.out("{} {} {}".format(latitude,longitude,altitude))
            time.sleep(1)


if __name__ == "__main__":
    mgr = Manager()
    mgr.start()