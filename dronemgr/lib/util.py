from . globals import Configuration

import MySQLdb
import time
import os
import ConfigParser


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
            "flavor": self.db.get(order_uid,"flavor","orders"),
            "destination": self.db.get(order_uid,"destination","orders"),
            "timestamp": self.db.get(order_uid,"timestamp","orders"),
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

    def status(self,uid,new_status):
        self.db.set(new_status,uid,"status","drones")

    def job(self,uid,new_job=None):
        self.db.set(new_job,uid,"job","drones")

    def command(self,uid, new_command):
        self.db.set(new_command,uid,"command","drones")