#!/usr/bin python3

"""Global values for Neuropia."""

class Configuration:
    CONFIG_PATH = "config/app.cfg"
    SOCKET_HOST = "0.0.0.0"
    SOCKET_PORT = 80
    THREAD_POOL = 12
    ERROR_LOG_PATH = "log/error.log"
    ACCESS_LOG_PATH = "log/access.log"

class NPSimConfig:
    HMAC = "a964153ae6a671bb77a9dce85f709eed"  # must match HMAC key at bottom of NPSim server.py
    NAME = "queuedaemon"
    HOST = "128.148.107.229"                   # ip address of NPSim machine
    PORT = 9090                                # LAN port where NPSim server is hosted
    SIMULATION_QUEUED = "Your simulation has been queued. You will receive a notification once it is completed."
    SIMULATION_EXISTS = "The simulation you are trying to run already exists!"
    START_MESSAGE = "SimDaemon started. Created %d processing threads."
    STOP_MESSAGE = "SimDaemon stopped. Total uptime was %.2f seconds."

class App:
    NAME = "Neuropia"
    VERSION = "v0.1.0"
    AUTHORS = "Benjamin Shanahan"
    AUTHOR_EMAILS = "benjamin_shanahan@brown.edu"
    URL = "http://www.neuropia.org"
    SHORT_URL = "Neuropia.org"
    DESCRIPTION = "Neural circuit simulator and teaching tool."
    LONG_DESCRIPTION = """long description here"""

class Database:
    HOST = "localhost"
    USER = "root"
    PASSWORD = ""
    DATABASE_NAME = "neuropia"

class Errors:
    GENERIC = {
        "general": "An error occurred.",
        "no_data": "No data was received."
    }
    LOGIN = {
        "general": "An error occurred during login.",
        "bad_username_password": "Invalid username or password.",
        "bad_username": "Username does not exist.",
        "bad_password": "Password does not match given username",
    }
    AUTHORIZATION = {
        "general": "An error occurred during authorization.",
        "unauthorized": "You are unauthorized to view this resource.",
    }
    REGISTRATION = {
        "general": "An error occurred during registration.",
    }
    DATABASE = {
        "general": "An error occurred during database connection.",
        "bad_query": "Unable to process query.",
    }
    SIMDAEMON = {
        "general": "Error processing simulation: %s.",
    }

class LogConst:
    LINEBREAK = "\n"
    MESSAGE_PREPEND = "   # "

class Pages:
    INDEX = {
        "id": "index",
        "href": "/",
        "caption": "Home"
    }
    SIMULATOR = {
        "id": "simulator",
        "href": "/simulator",
        "caption": "Simulator"
    }
    DOCS = {
        "id": "docs",
        "href": "/docs",
        "caption": "Docs"
    }
    ABOUT = {
        "id": "about",
        "href": "/about",
        "caption": "About"
    }
    SEARCH = {
        "id": "search",
        "href": "/about",
        "caption": "Search"
    }
    LOGIN = {
        "id": "login",
        "href": "/login",
        "caption": "Login"
    }
    REGISTER = {
        "id": "register",
        "href": "/login?default=register",
        "caption": "Register New Account"
    }
    LOGOUT = {
        "id": "logout",
        "href": "/logout",
        "caption": "Logout"
    }
    PROFILE = {
        "id": "profile",
        "href": "/profile",
        "caption": "My Profile"
    }
    ADMIN = {
        "id": "admin",
        "href": "/admin",
        "caption": "Admin"
    }
    PAGE_LIST = [  # keep this up-to-date (it is what allows site linking and navigation)
        INDEX,
        SIMULATOR,
        DOCS,
        ABOUT,
        SEARCH,
        LOGIN,
        REGISTER,
        LOGOUT,
        PROFILE,
        ADMIN
    ]

class Templates:
    TEMPLATE_PATH = {
        "404": "404.html",
        "500": "500.html",
        "index": "view/page/index.html",
        "about": "view/page/about.html",
        "simulator": "view/page/simulator.html",
        "docs": "view/page/docs.html",
        "search": "view/page/search.html",
        "login": "view/page/login.html",
        "profile": "view/page/profile.html",
        "admin": "view/page/admin.html",
    }

class Authorization:
    AUTH_REQUIRE = "auth.require"  # variable name in CherryPy config
    SESSION_KEY = "_username"
    AUTH_LEVELS = {
        "user": 1,
        "moderator": 2,
        "admin": 3
    }
