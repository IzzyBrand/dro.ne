from jinja2 import Environment, FileSystemLoader

from . util import DBFunc, UID, Timestamp, Web
from . globals import Session, Pages, App

import random
import string
import cherrypy
import json

# Instantiate database query object
DB = DBFunc()  

# Database table string names
DRONES = "drones"
ZONES = "zones"
TYPES = "types"

""" The Controller object serves pages to the client when the site is visited """
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
            status = DB.authenticate_user(username,password)
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


""" The API object enables realtime requests of drone state """
@cherrypy.expose
class API(object):

    """ Return JSON array of information to authorized client when requested """
    @cherrypy.tools.accept(media="application/json")
    def GET(self, uid=None, subset=None):
        # If UID is specified, return information specific to that UID. If UID is
        # specified, information contained in subset will be returned to client.
        # Possible options are:
        #    position, type, zone, all, None (returns command)
        if uid is not None and DB.uid_exists(uid,DRONES):
            
            def _get_position(uid):
                return {
                    "latitude": DB.get("latitude",DRONES,uid),
                    "longitude": DB.get("longitude",DRONES,uid),
                    "altitude": DB.get("altitude",DRONES,uid),
                    "speed": DB.get("speed",DRONES,uid),
                    "timestamp": DB.get("timestamp",DRONES,uid)
                }

            def _get_type(uid):
                type_uid = DB.get("type",DRONES,uid)
                return {
                    "maxpayload": DB.get("maxpayload",TYPES,type_uid),
                    "minvoltage": DB.get("minvoltage",TYPES,type_uid),
                    "topspeed": DB.get("topspeed",TYPES,type_uid)
                }

            def _get_zone(uid):
                zone_uid = DB.get("zone",DRONES,uid)
                return {
                    "latitude": DB.get("latitude",ZONES,zone_uid),
                    "longitude": DB.get("longitude",ZONES,zone_uid),
                    "altitude": DB.get("altitude",ZONES,zone_uid)
                }

            def _get_command(uid):
                return {"command": DB.get("command",DRONES,uid)}

            def _get_all(uid):
                return {
                    "command": _get_command(uid),
                    "position": _get_position(uid),
                    "type": _get_type(uid),
                    "zone": _get_zone(uid)
                }

            # Return requested subset to client
            cherrypy.response.status = 200  # OK
            if subset is None:
                # Return command
                return json.dumps(_get_command(uid))
            elif subset == "position":
                # Return information related to drone position
                return json.dumps(_get_position(uid))
            elif subset == "type":
                # Return information related to drone type
                return json.dumps(_get_type(uid))
            elif subset == "zone":
                # Return information related to drone destination (landing zone)
                return json.dumps(_get_zone(uid))
            elif subset == "all":
                # Return all information
                return json.dumps(_get_all(uid))
            else:
                # Return empty json
                return "{}"

        else:  # if no UID is specified, return a list of all drone UIDs
            
            uids = DB.get_all("uid",DRONES)
            ret = {"uids":[]}
            for u in uids:
                ret["uids"].append(u[0])
            cherrypy.response.status = 200  # OK
            return json.dumps(ret)

    """ Parse drone state (JSON array) from authorized client and updated database """
    def POST(self, uid=None, auth=None, state=None):
        if uid is not None and auth is not None and state is not None \
        and DB.uid_exists(uid,DRONES) and DB.authorized(uid,auth):
            # Determine which values are included in state (allows partial updates)
            # and then only update those values
            state = json.loads(state)  # convert to dictionary
            for key, value in state.iteritems():
                DB.set(key, value, DRONES, uid)
            cherrypy.response.status = 201  # Created
            return json.dumps(state)
        else:
            cherrypy.response.status = 401  # Unauthorized
            return "Unauthorized"