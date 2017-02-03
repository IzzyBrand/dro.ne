#!/usr/bin python3

"""Utility classes for Neuropia."""

from lib.globals import LogConst, Authorization, App, Pages

import cherrypy
import hashlib, sha3
import json
import os, time


"""Functions for querying MySQL database."""
class DBFunc:

    # Check to see if username exists in database.
    @classmethod  # use this decorator to make the method accessible directly via class name
    def username_exists(self, username):
        out = self._query(self, "SELECT name FROM users WHERE username = %s", (username,))
        return len(out) is not 0

    # Add new user to database. User info passed to function via dict.
    @classmethod
    def add_user(self, name, username, password_hash, email, groupname):
        q = "INSERT INTO users (name,username,password_hash,email,groupname) VALUES (%s,%s,%s,%s,%s)"
        v = (name,username,password_hash,email,groupname,)
        success = self._query(self, q, v, return_data=False)
        if not success:
            Logging.out("Encountered error adding new user (%s, attempted username: %s) to database." % (name, username))
        else:
            Logging.out("Registered new user: %s (%s)" % (name, username));
        return success

    # Compare password hash with database password_hash entry.
    @classmethod
    def check_password(self, username, password_hash):
        return password_hash == self._get_password_hash(self, username)

    # Get user's full name from their username.
    @classmethod
    def get_name(self, username):
        out = self._query(self, "SELECT name FROM users WHERE username = %s", (username,))
        return out

    # Get user's email from their username.
    @classmethod
    def get_email(self, username):
        out = self._query(self, "SELECT email FROM users WHERE username = %s", (username,))
        return out

    # Get user's groupname from their username.
    @classmethod
    def get_groupname(self, username):
        out = self._query(self, "SELECT groupname FROM users WHERE username = %s", (username,))
        return out

    # Utility function to query database.
    def _query(self, q, v, return_data=True, return_idx=0, return_all=False):
        connection = cherrypy.thread_data.db  # get db connection
        cursor = connection.cursor()  # get cursor to execute SQL queries
        connection.ping(True)  # ping database to make sure it is connected TODO change this if we are still getting 'MySQL server has gone away' error after 8 hours inactive
        cursor.execute(q,v)
        if return_data:
            rows = cursor.fetchall()
            cursor.close()
            if not return_all and len(rows) > 0:  # only return from first row
                return rows[0][return_idx]
            else:  # return all data or if result is empty
                return rows
        else:
            cursor.close()
            try:
                connection.commit()  # save inserted data into database
                return True
            except:
                connection.rollback()  # reverse and remove any changes if error
                logging.out("Encountered error while trying to commit data to database table.")
                return False

    # Get user's password_hash from their username.
    def _get_password_hash(self, username):
        out = self._query(self, "SELECT password_hash FROM users WHERE username = %s", (username,))
        return out


"""General HTTP and loading functions."""
class General:

    @classmethod
    # Load JSON file and return it.
    def get_json(self, path):
        with open(path) as f:
            info = json.load(f)
        return info
        
    @classmethod
    # Get page info to pass to each page
    def get_page_info(self):
        info = {
            "name": App.NAME,
            "version": App.VERSION,
            "authors": App.AUTHORS,
            "author_emails": App.AUTHOR_EMAILS,
            "url": App.URL,
            "short_url": App.SHORT_URL,
            "description": App.DESCRIPTION,
            "long_description": App.LONG_DESCRIPTION,
            "page": Pages.PAGE_LIST
        }
        return info

    # Redirect user to different page.
    @classmethod
    def redirect(self, page):
        raise cherrypy.HTTPRedirect(page)

    # Force user to login before accessing a resource. Reroutes user with reroute().
    @classmethod
    def force_login(self, origin):
        self._reroute(self, Pages.LOGIN["href"], origin=origin)

    # Parameter "origin" is passed to "page" via "get" protocol.
    def _reroute(self, page, origin):
        raise cherrypy.HTTPRedirect(page + "?origin=" + origin)


"""Authorization checking for user access to different pages."""
class Auth:

    # Check authorization of a given username and return if user can access resource.
    def check(username, require_groupname=None):
        notempty = username is not None and username != ""
        exists = DBFunc.username_exists(username)
        group_okay = True
        if require_groupname is not None:
            groupname = DBFunc.get_groupname(username)
            group_okay = groupname == require_groupname
        return notempty and exists and group_okay


"""Hashing functions."""
class Hash:

    # Generate SHA-3 hash of given string.
    def hashstr(data_string, encoding="UTF-8"):
        bytestring = bytes(data_string, encoding=encoding)
        s = hashlib.sha3_512()
        s.update(bytestring)
        return s.hexdigest()


"""Logging functions."""
class Logging:

    # Output message to server log.
    # TODO update this method so that it actually works
    def log(msg):
        console(msg)

    # Output message to console.
    def console(msg):
        print(LogConst.MESSAGE_PREPEND, msg)


"""Filesystem management functions."""
class ManageFS:

    # Finds last modified file in given path. Default path is the current directory.
    #
    # Function returns dict containing directory, filename, and last modification time
    # of most recently modified file.
    def get_last_modified(path="."):
        max_mtime = 0
        for dirname,subdirs,files in os.walk(path):
            for fname in files:
                full_path = os.path.join(dirname, fname)
                mtime = os.stat(full_path).st_mtime
                if mtime > max_mtime:
                    max_mtime = mtime
                    max_dir = dirname
                    max_file = fname
        
        # Format max_mtime time string to something readable
        time_formatted = time.strftime('%m/%d/%Y at %I:%M:%S %p', time.localtime(max_mtime))
        
        return {
            "time": time_formatted,
            "dir": max_dir,
            "file": max_file,
        }


"""Search functions."""
class Search:

    # Search within a file for a string and return boolean indicating presence of string
    def file(fi, str):
        with open(fi) as f:
            contents = f.read()
            return str in contents

    # Search within a directory for a string and return list of files containing the string
    def dir(dir, str, include_subdir=True):
        pass


"""Session management functions."""
class Session:

    """Returns dict containing information based on session variable, username."""
    def info():
        username = cherrypy.session.get(Authorization.SESSION_KEY)
        out = {
            "username": username,
            "name": DBFunc.get_name(username),
            "email": DBFunc.get_email(username),
            "groupname": DBFunc.get_groupname(username)
        }
        return out