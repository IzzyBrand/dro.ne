from lib.util import Status, DBFunc
from lib.controllers import Controller
from lib.globals import Timing, Configuration

import os
import time
import signal
import sys

"""
Manager (just a state machine) that delegates and manages deployed
drones, etc.

The main focus of this manager is to coordinate all of the
management subfunctions as well as make database calls.
"""
class Manager:

    def __init__(self):
        self.running = True
        self.controller = Controller()

    # Start manager
    def start(self):
        Status.out("Manager started")
        signal.signal(signal.SIGINT, self.signal_handler)
        self.block()

    # Stop manager
    def stop(self):
        Status.out("Stopping manager")
        self.running = False

    # Run when Ctrl-C is pressed
    def signal_handler(self, signal, frame):
        self.stop()

    # Block manager
    def block(self):
        while self.running:
            self.controller.step()
            time.sleep(Timing.UPDATE_INTERVAL)


def print_pid(path):
    pid = os.getpid()
    try:
        pidfile = open(path,"wb")
        output = "dronesvrpid='" + str(pid) + "'"
        pidfile.write(output)  # write PID to text file
    finally:
        try:
            pidfile.close()
        except:
            pass


if __name__ == "__main__":
    print_pid(Configuration.SERVER_PID_PATH)
    mgr = Manager()
    mgr.start()