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

    ################################
    ### Data retrieval functions ###
    ################################

    def set(self,new_val,uid,field,table):
        self._query("UPDATE {} SET {}='{}' WHERE uid='{}'".format(table,field,new_val,uid),ret_data=False)

    def get(self,uid,field,table):
        return self._query("SELECT {} FROM {} WHERE uid='{}'".format(field,table,uid))

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