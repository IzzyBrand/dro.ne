from . globals import Database
from . util import DBFunc

import cherrypy
import json

# Instantiate database query object
DB = DBFunc()  

# Names of database tables
DRONES = Database.DRONE_TABLE
ZONES = Database.ZONE_TABLE
TYPES = Database.TYPE_TABLE

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
            # print "{}, {}, {}".format(uid,auth,state)  # debug only
            cherrypy.response.status = 401  # Unauthorized
            return "Unauthorized"

    """ Queue new request (user request for a drone pickup / dropoff) """
    def QUEUE(self, username=None, password=None, request=None):
        if username is not None and password is not None:
            # Authenticate username and password. Allow both user and admin credentials.
            if DB.authenticate_user("user",username,password) or \
            DB.authenticate_user("admin",username,password):
                print "User authenticated."
            else:
                print "User does not exist!"