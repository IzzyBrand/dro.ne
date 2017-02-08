from . globals import Database

import MySQLdb
import time
import os


""" Database management functions """
class DBFunc:

    def __init__(self):
        self.db = MySQLdb.connect(
            Database.HOST,
            Database.USER,
            os.environ[Database.PWD_ENV_VAR],
            Database.DB_NAME)
        self.uid = None

    def set_uid(self,uid):
        self.uid = uid

    def get_uid(self):
        return self.uid

    def get_drone(self,field):
        return self._get(field,"drones")

    def get_zone(self,field):
        return self._get(field,"zones")

    def get_type(self,field):
        return self._get(field,"types")

    def _get(self,field,table):
        if self.uid is None:
            raise Exception("Please set UID prior to requested value from database.")
        return self._query("SELECT {} FROM {} WHERE uid='{}'".format(field,table,self.uid))

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