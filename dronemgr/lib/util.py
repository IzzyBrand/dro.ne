from . globals import Configuration, UIDConst

import MySQLdb
import time
import os
import ConfigParser
from dateutil import parser
from datetime import datetime


""" Database management functions """
class DBFunc:


    def __init__(self):
        cfg = ConfigParser.ConfigParser()
        cfg.read(Configuration.DB_AUTH_PATH)  # parse .keys file in config/ dir
        self.db = MySQLdb.connect(
            cfg.get("Database","host"), 
            cfg.get("Database","user"), 
            cfg.get("Database","password"),
            cfg.get("Database","database"))
        self.uid = UID()

    ################################
    ### Data retrieval functions ###
    ################################

    def uid_exists(self,uid,table):
        r = self._query("SELECT uid FROM {} WHERE uid='{}'".format(table,uid))
        return len(r) is not 0

    def set(self,new_val,uid,field,table):
        self._query("UPDATE {} SET {}='{}' WHERE uid='{}'".format(table,field,new_val,uid),ret_data=False)

    def get(self,uid,field,table):
        return self._query("SELECT {} FROM {} WHERE uid='{}'".format(field,table,uid))

    def delete(self,uid,table):
        self._query("DELETE FROM {} WHERE uid='{}'".format(table,uid))

    def get_all(self,field,table):
        res = self._query("SELECT {} FROM {}".format(field,table),ret_all=True)
        ret = []
        for val in res:
            ret.append(val[0])
        return ret

    # inserts a new task into the task table and returns the uid of the task
    def add_task(self, task):
        task['uid'] = self._new_uid('task') # generate a new uid for the task
        keys = ",".join(task.keys())
        vals = "','".join(task.values())  # joins values with quotes (start & end don't have quotes)
        sql = "INSERT INTO tasks ({}) VALUES ('{}')".format(keys,vals)
        if self._query(sql,return_data=False): return task['uid']
        else: return None

    #################################
    ### Database helper functions ###
    #################################

    # Query the database
    def _query(self,q,ret_data=True,ret_all=False,ret_row=0):
        self.db.ping(True)  # refresh connection to db if it has gone away
        cursor = self.db.cursor()  # get cursor
        cursor.execute(q)
        self.db.commit()  # commit to db
        if ret_data:
            rows = cursor.fetchall()
            if not ret_all and len(rows) > 0:
                # only return data from row ret_row
                return rows[0][ret_row]
            else:
                # return all data or if result is empty
                return rows
        cursor.close()

    # generate a new uid and verify that it is unique to that table
    def _new_uid(self, uid_type):
        new_uid = self.uid.generate(uid_type)
        while self._uid_exists(new_uid, uid_type):
            new_uid = self.uid.generate(uid_type)
        return new_uid

    # check if a uid exists in the table
    def _uid_exists(self, uid, table):
        r = self._query("SELECT uid FROM {} WHERE uid=%s".format(table),(uid,))
        return len(r) is not 0

""" Generic status print reporting """
class Status:

    @classmethod
    def out(self,msg):
        t = time.strftime("%Y-%m-%d %H:%M:%S")
        print "[{}] {}".format(t,msg)


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

    def order(self,order_uid):
        return {
            "uid": order_uid,
            "flavor": self.db.get(order_uid,"flavor","orders"),
            "destination": self.db.get(order_uid,"destination","orders"),
            "timestamp": parser.parse(self.db.get(order_uid,"timestamp","orders")),
            "departuretime": self.db.get(order_uid,"departuretime","orders"),
            "arrivaltime": self.db.get(order_uid,"arrivaltime","orders"),
            "completed": self.db.get(order_uid,"completed","orders")
        }

    # Return list of all incompleted orders from database (or completed depending on arg flag)
    def list(self,field,table,completed=None):
        if not completed:
            return self.db.get_all(field,table)
        else:
            res = self.db._query("SELECT {} FROM {} WHERE completed='{}'".format(field,table,completed),ret_all=True) 
            ret = []
            for val in res:
                ret.append(val[0])
            return ret



""" Set information in database """
class Set:

    def __init__(self,db):
        self.db = db

    def task(self,drone_uid,task_uid):
        self.db.set(task_uid,drone_uid,"task","drones")

    def status(self,drone_uid, status):
        self.db.set(status, drone_uid, 'status', 'drones')

    def command(self,drone_uid,new_command):
        self.db.set(new_command,drone_uid, "command","drones")

""" Generate consistent UIDs """
class UID:
    # Generate UID
    # Example usage: UID.generate("drone") or UID.generate("zone")
    @classmethod
    def generate(self,uid_type):
        randStr = "".join(random.sample(string.hexdigits, int(UIDConst.LENGTH)))
        if uid_type == "drone":
            c = UIDConst.DRONE_ID
        elif uid_type == "tast":
            c = UIDConst.TAST_ID
        elif uid_type == "type":
            c = UIDConst.TYPE_ID
        elif uid_type == "order":
            c = UIDConst.ORDER_ID
        return c + randStr
