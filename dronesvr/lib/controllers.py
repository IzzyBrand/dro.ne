from jinja2 import Environment, FileSystemLoader

from . util import DBFunc, UID, Timestamp, Web, Secure
from . globals import Session, Pages, App, Database

import random
import string
import cherrypy
import json

# Instantiate database query object
DB = DBFunc()  

# Names of database tables
DRONES = Database.DRONES_TABLE
ZONES = Database.ZONES_TABLE
TYPES = Database.TYPES_TABLE

"""
The Controller class serves the requested page to the client (given a number of
criteria). It handles both the login-required administrative page and the realtime
user front-end of the site.
"""
class Controller(object):

    """ Landing pages """
    # Site index (shows login for admin page)
    @cherrypy.expose
    def index(self):
        tmpl = Environment(loader=FileSystemLoader(".")).get_template(Pages.TEMPLATE["index"])
        username = cherrypy.session.get(Session.AUTH_KEY)
        if username is not None:
            raise Web.redirect(Pages.URL["admin"])
        else:
            page_data = self._get_page_data()
            return tmpl.render(page_data)
    # Admin landing page (allows database modification)
    @cherrypy.expose
    def admin(self, status=None, action=None, **kwargs):
        tmpl = Environment(loader=FileSystemLoader(".")).get_template(Pages.TEMPLATE["admin"])
        username = cherrypy.session.get(Session.AUTH_KEY)
        if username is not None:
            if action is not None or action == "":
                status = self._delegate_action(action, kwargs)
                raise Web.redirect(Pages.URL["admin"] + "?status=%s" % status)
            page_data = self._get_page_data(username,status)
            return tmpl.render(page_data)
        else:
            raise Web.redirect(Pages.URL["index"])

    """ Functional endpoints """
    # Login endpoint (checks POSTed credentials and then redirects)
    @cherrypy.expose
    def login(self, username=None, password=None, **kwargs):
        if username is not None and password is not None:
            # check that username is safe before doing anything with database
            if Secure.credentials(username):
                status = DB.authenticate_user(username,password,req_type=2)  # requires admin credentials
                if status:
                    cherrypy.session[Session.AUTH_KEY] = username
                    raise Web.redirect(Pages.URL["admin"])
                else:
                    raise Web.redirect(Pages.URL["index"])
        cherrypy.session[Session.AUTH_KEY] = None
        raise Web.redirect(Pages.URL["index"])
    # Logout endpoint (removes logged-in user session and redirects)
    @cherrypy.expose
    def logout(self):
        cherrypy.session[Session.AUTH_KEY] = None
        raise Web.redirect(Pages.URL["index"])

    """ Helper functions """
    # Return page_data dict to pass to Jinja template
    def _get_page_data(self, username=None, status=None):
        page_data = {
            "info": App.INFO
        }
        if username is not None:  # this means username exists and is valid
            # TODO: fix this, it's really hacky:
            drones_fields = DB.get_fields(DRONES)
            types_fields = DB.get_fields(TYPES)
            zones_fields = DB.get_fields(ZONES)
            drones_fields = drones_fields[1:5]  # only display fields 1-5 to user
            types_fields = types_fields[1:]  # skip UID field
            zones_fields = zones_fields[1:]
            page_data["username"] = username
            page_data["nickname"] = DB.get_user_info("nickname",username)
            page_data["email"] = DB.get_user_info("email",username)
            page_data["phone"] = DB.get_user_info("phone",username)
            page_data["uids"] = DB.get_values("uid",DRONES)  # send a list of drone UIDs for building our display grid
            page_data["drones_fields"] = drones_fields
            page_data["zones_fields"] = zones_fields
            page_data["types_fields"] = types_fields
            page_data["status"] = "" if status is None else status
        return page_data
    # Delegate administrative database modifying actions
    def _delegate_action(self, action, args):
        if action == "new-drone":
            uid = UID.generate("drone")
            # TODO: add drone
            return "Added new drone, {}.".format(uid)
        elif action == "new-type":
            uid = UID.generate("type")
            # TODO: add type
            return "Added new drone type, {}.".format(uid)
        elif action == "new-zone":
            uid = UID.generate("zone")
            # TODO: add zone
            return "Added new landing zone, {}.".format(uid)
        elif action =="remove-uid":
            for table in [DRONES,TYPES,ZONES]:
                if DB.uid_exists(args["uid"],table):
                    DB.delete(args["uid"],table)
                    return "Removed UID {} from {}.".format(args["uid"],table)
            return "UID not found. No action was taken."
        else:
            return ""