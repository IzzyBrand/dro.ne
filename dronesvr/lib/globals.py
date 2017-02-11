class Configuration:
    CONFIG_PATH = "config/app.config"
    SOCKET_HOST = "0.0.0.0"
    SOCKET_PORT = 80
    THREAD_POOL = 12
    ERROR_LOG_PATH = "log/error.log"
    ACCESS_LOG_PATH = "log/access.log"


class App:
    INFO = {
        "name": "Air Control Server",
        "version": "v1.0",
        "authors": "Benjamin Shanahan",
        "author_emails": "benjamin_shanahan@brown.edu",
        "full_url": "",
        "short_url": "",
        "description": "Air control server for real-time drone management",
        "long_description": """long description here"""
    }

class Database:
    HOST = "localhost"
    USER = "root"
    PASSWORD_ENV_VAR = "DRONE_DB_PWD"  # name of environmental variable
    DATABASE_NAME = "dronedb"
    DRONE_TABLE = "drones"
    ZONE_TABLE = "zones"
    TYPE_TABLE = "types"
    QUEUE_TABLE = "queue"
    USER_TABLE = "user"

class UIDConst:
    LENGTH = 7  # total length, NOT including hardcoded values below
    DRONE_ID = "D"  # at beginning of each drone UID
    ZONE_ID = "Z"  # at beginning of each zone UID
    TYPE_ID = "T"  # at beginning of each type UID
    JOB_ID = "J"  # at beginning of each job UID (in queue)  

class Pages:
    # Path to template file
    TEMPLATE = {
        "index": "view/page/index.html",
        "admin": "view/page/admin.html"
    }
    # URL to page
    URL = {
        "index": "/",
        "admin": "/admin"
    }

class Session:
    AUTH_KEY = "_username"

class Errors:
    GENERIC = {
        "general": "An error occurred",
        "no_data": "No data was received"
    }
    API = {
        "general": "An error occurred while contacting endpoint",
    }
    DATABASE = {
        "general": "An error occurred during database connection",
        "bad_query": "Unable to process query",
    }