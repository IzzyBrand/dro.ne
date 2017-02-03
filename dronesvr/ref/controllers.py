#!/usr/bin python3

""" Controller Class Objects

Benjamin Shanahan, 20150610.

Controller serves pages to user and ErrorController serves custom error pages.
"""

from . globals import Templates, Authorization, Pages, Errors, NPSimConfig
from . util import DBFunc, Session, ManageFS, General, Hash, Auth, Logging

from lib.tool.template import JinjaLoader
from jinja2 import Environment, FileSystemLoader
from Pyro4 import Proxy

import json
import cherrypy
import uuid

# Load general info to pass to each page
info = General.get_page_info()
info["last_mod"] = ManageFS.get_last_modified()


# Matlab testing
#import matlab.engine
#eng = matlab.engine.start_matlab()
#eng.cd(r"C:/Users/Ben/Desktop/CherryPy/Neuropia/neuropia/lib/m/", nargout=0)


"""Page generation handling."""
class Controller(object):

    #####################
    ## MAIN SITE PAGES ##
    #####################
    
    @cherrypy.expose
    @cherrypy.tools.jinja(template=Templates.TEMPLATE_PATH["index"])
    def index(self, **params):
        page_data = {"info": info, "session": Session.info()}
        return page_data
    
    @cherrypy.expose
    @cherrypy.tools.jinja(template=Templates.TEMPLATE_PATH["about"])
    def about(self, **params):
        page_data = {"info": info, "session": Session.info()}
        return page_data
    
    @cherrypy.expose
    @cherrypy.tools.jinja(template=Templates.TEMPLATE_PATH["simulator"])
    def simulator(self, **params):
        page_data = {"info": info, "session": Session.info()}
        return page_data

    @cherrypy.expose
    @cherrypy.tools.jinja(template=Templates.TEMPLATE_PATH["docs"])
    def docs(self, **params):
        page_data = {"info": info, "session": Session.info()}
        return page_data
    
    @cherrypy.expose
    @cherrypy.tools.jinja(template=Templates.TEMPLATE_PATH["search"])
    def search(self, q=None, **params):
        results = [
            ('The first search result','Here is a short description describing the search result.','/'),
            ('The second search result','Here is a short description describing the search result.','/'),
        ]
        page_data = {
            "info": info,
            "session": Session.info(),
            "title": "Search",
            "q": q,
            "results": results,
        }
        return page_data
    
    @cherrypy.expose
    @cherrypy.tools.jinja(template=Templates.TEMPLATE_PATH["login"])
    def login(self, action=None, origin="", default="login", **params):
        session = Session.info()
        if session["username"] is not None:
            General.redirect(Pages.PROFILE["href"])
        page_data = {
            "info": info,
            "session": session,
            "default_tab": default,
            "origin": origin
        }
        if action == "v_new":
            page_data["default_tab"] = "register"
            # Validate and add new user to database
            inputs = dict(params)
            name = inputs["name"] if "name" in inputs else None
            username = inputs["username"] if "username" in inputs else None
            password_hash = Hash.hashstr(inputs["password"]) if "password" in inputs else None
            email = inputs["email"] if "email" in inputs else None
            if name is not None and username is not None and password_hash is not None and email is not None:
                if DBFunc.add_user(name, username, password_hash, email, "user"):
                    # registration successful: update session, redirect to profile
                    cherrypy.session[Authorization.SESSION_KEY] = username
                    if origin != "":
                        General.redirect(origin)
                    else:
                        General.redirect(Pages.PROFILE["href"])
                else:
                    page_data["registration_error"] = Errors.REGISTRATION["general"]
        elif action == "v_exi":
            page_data["default_tab"] = "login"
            # Check login for validity and pass user to profile page
            inputs = dict(params)
            username = inputs["username"] if "username" in inputs else None
            password_hash = Hash.hashstr(inputs["password"]) if "password" in inputs else None
            if username is not None and password_hash is not None:
                if DBFunc.username_exists(username) and DBFunc.check_password(username, password_hash):
                    # log in successful: update session, redirect to profile
                    cherrypy.session[Authorization.SESSION_KEY] = cherrypy.request.login = username
                    if origin != "":
                        General.redirect(origin)
                    else:
                        if DBFunc.get_groupname(username) == "admin":
                            General.redirect(Pages.ADMIN["href"])
                        else:
                            General.redirect(Pages.PROFILE["href"])
                else:
                    page_data["login_error"] = Errors.LOGIN["bad_username_password"]
        return page_data

    @cherrypy.expose
    def logout(self):
        username = cherrypy.session.get(Authorization.SESSION_KEY, None)
        cherrypy.session[Authorization.SESSION_KEY] = None
        if username is not None:
            cherrypy.request.login = None
        General.redirect(Pages.INDEX["href"])

    @cherrypy.expose
    @cherrypy.tools.jinja(template=Templates.TEMPLATE_PATH["profile"])
    def profile(self, **params):
        session = Session.info()
        if Auth.check(session["username"]):
            inputs = dict(params)
            update = inputs["update"] if "update" in inputs else None
            page_data = {"info": info, "session": session}
            if update is not None:
                page_data["update"] = update
            return page_data
        else:
            General.force_login(Pages.PROFILE["id"])

    # These may prove to be useful for administrative purposes:
    #    cherrypy.engine.restart()
    #    cherrypy.engine.exit()
    @cherrypy.expose
    @cherrypy.tools.jinja(template=Templates.TEMPLATE_PATH["admin"])
    def admin(self, **params):
        session = Session.info()
        if Auth.check(session["username"], require_groupname="admin"):
            inputs = dict(params)
            update = inputs["update"] if "update" in inputs else None
            page_data = {"info": info, "session": session}
            if update is not None:
                page_data["update"] = update
            return page_data
        else:
            General.force_login(Pages.ADMIN["id"])


    ################################################
    ## BACKEND PAGES FOR PROCESSING USER REQUESTS ##
    ################################################
    
    # Serve ajax request helper pages
    @cherrypy.expose
    def ajax(self, route=None, **params):
        if route is None:
            General.redirect(Pages.INDEX["href"])
        elif route == "username_exists":
            inputs = dict(params)
            username = inputs["username"] if "username" in inputs else None
            if username is not None:
                return "true" if DBFunc.username_exists(username) else "false"
        elif route == "queue_job":

            # TODO - update this if-block to check for simulation pre-existence.
            #        if simulation does not exist, queue it in processing pool
            #        else if simulation exists, serve it to the user.
            #
            # Note:  For now, the code recognizes every new simulation as being
            #        unique and will freshly compute everything.

            if params is not None and params != "" and "data" in dict(params):
                input_data = json.loads(dict(params)["data"])
            else:
                input_data = None  # nothing received by ajax, so do nothing
            if input_data is not None:
                exists = False
                if not exists:
                    try:
                        uid = uuid.uuid4()
                        hmac = NPSimConfig.HMAC
                        name = NPSimConfig.NAME
                        host = NPSimConfig.HOST
                        port = NPSimConfig.PORT
                        with Proxy("PYRO:%s@%s:%d" % (name, host, port)) as queuedaemon:
                            queuedaemon._pyroHmacKey = hmac
                            queuedaemon.add_job(uid, input_data)
                        return NPSimConfig.SIMULATION_QUEUED
                    except Exception as e:
                        Logging.console(Errors.SIMDAEMON["general"] % e)
                        return Errors.SIMDAEMON["general"] % e
                else:
                    return NPSimConfig.SIMULATION_EXISTS
            else:
                return Errors.GENERIC["no_data"]
        else:
            return


"""Error page controller to handle error page generation."""
class ErrorController(object):
    def error_404(status, message, traceback, version):
        tmpl = Environment(loader=FileSystemLoader("view/")).get_template(Templates.TEMPLATE_PATH["404"])
        page_data = {
            "info": info,
            "session": Session.info(),
            "title": "404 Error",
            "status": status,
            "message": message,
        }
        return tmpl.render(page_data)
        
    def error_500(status, message, traceback, version):
        tmpl = Environment(loader=FileSystemLoader("view/")).get_template(Templates.TEMPLATE_PATH["500"])
        page_data = {
            "info": info,
            "session": Session.info(),
            "title": "500 Error",
            "status": status,
            "message": message,
        }
        return tmpl.render(page_data)