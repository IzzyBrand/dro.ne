from . globals import UIDConst, Errors, Database

import string
import random
import datetime
import cherrypy
import hashlib


"""Functions for querying MySQL database."""
class DBFunc:

    # Check if user exists in ADMIN table
    def _user_exists(self, username):
        r = self._query("SELECT username FROM admin WHERE username='{}'".format(username))
        return len(r) is not 0

    # Check if user exists, and if so, compare the md5 hash
    # of the given password with that stored in ADMIN table for
    # specified username
    def authenticate_user(self, username, password):
        if self._user_exists(username):
            pwd_hash = self._query("SELECT password FROM admin WHERE username='{}'".format(username))
            if pwd_hash == Encoding.md5(password):
                return True
            else:
                return False

    # Retrieve user specific data from ADMIN table
    def get_user_info(self, field, username):
        return self._query("SELECT {} FROM admin WHERE username='{}'".format(field,username))

    # Verify that given UID exists in TABLE
    # Example usage: DBFunc.exists("D2Da037d","drones")
    def uid_exists(self, uid, table):
        r = self._query("SELECT uid FROM {} WHERE uid='{}'".format(table,uid))
        return len(r) is not 0

    # Check that the provided AUTH hash code matches that which 
    # we have in our database for the given UID
    # Example usage: DBFunc.authorized("D2Da037d","fe3d1760dfad167b51b4ffc60f8bbefe")
    def authorized(self, uid, auth, table="drones"):
        r = self._query("SELECT auth FROM {} WHERE uid='{}'".format(table,uid))
        return r == auth

    # Return a list of all values within a given field of a given table
    def get_values(self, field, table):
        tmp = []
        for t in self.get_all(field,table):
            tmp.append(t[0])
        return tmp

    # Return a list of all fields within a given table
    def get_fields(self, table):
        tmp = []
        q = self._query("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='{}' AND TABLE_NAME='{}';".format(Database.DATABASE_NAME,table), return_all=True)
        for t in q:
            tmp.append(t[0])
        return tmp

    # Get value contained in FIELD from TABLE in row matching UID
    # Example usage: DBFunc.get("name","drones","D2Da037d")
    def get(self, field, table, uid):
        return self._query("SELECT {} FROM {} WHERE uid='{}'".format(field,table,uid))

    # Set value of FIELD within TABLE in row matching UID
    # Example usage: DBFunc.set("name","Gregg","drones","D2Da037d")
    def set(self, field, value, table, uid):
        return self._query("UPDATE {} SET {}='{}' WHERE uid='{}'".format(table,field,value,uid), return_data=False)

    # Get all values from all FIELDS in TABLE
    # Example usage: DBFunc.get_all("uid","drones")
    def get_all(self, field, table):
        return self._query("SELECT {} FROM {}".format(field,table), return_all=True)

    # Insert new row with UID into TABLE
    # Example usage: DBFunc.insert("0jFJdaam27","zones")
    def insert(self, uid, table):
        return self._query("INSERT INTO {} (uid) VALUES ('{}'')".format(table,uid), return_data=False)

    # Delete row matching UID in TABLE
    def delete(self, uid, table):
        self._query("DELETE FROM {} WHERE uid='{}'".format(table,uid), return_data=False)

    # Generic database query function
    def _query(self, q, return_data=True, return_idx=0, return_all=False):
        connection = cherrypy.thread_data.db  # get db connection
        connection.ping(True)  # this should refresh the connection to the database if it has timed out: http://www.neotitans.com/resources/python/mysql-python-connection-error-2006.html
        cursor = connection.cursor()  # get cursor to execute SQL queries
        cursor.execute(q)
        connection.commit()  # save inserted data into database

        if return_data:
            rows = cursor.fetchall()
            if not return_all and len(rows) > 0:  # only return from first row
                return rows[0][return_idx]
            else:  # return all data or if result is empty
                return rows

        cursor.close()


""" Generate consistent UIDs """
class UID:

    # Generate UID
    # Example usage: UID.generate("drone") or UID.generate("zone")
    @classmethod
    def generate(self,uid_type):
        randStr = "".join(random.sample(string.hexdigits, int(UIDConst.LENGTH)))
        if uid_type == "drone":
            c = UIDConst.DRONE_ID
        elif uid_type == "zone":
            c = UIDConst.ZONE_ID
        elif uid_type == "type":
            c = UIDConst.TYPE_ID
        return c + randStr


""" Get current timestamp """
class Timestamp:

    # Get current timestamp
    @classmethod
    def now(self):
        return str(datetime.datetime.now())


""" Generate various encodings of string """
class Encoding:

    @classmethod
    def md5(self, msg):
        m = hashlib.md5()
        m.update(msg)
        return m.hexdigest()


""" General web commands """
class Web:

    @classmethod
    def redirect(self, page):
        raise cherrypy.HTTPRedirect(page)