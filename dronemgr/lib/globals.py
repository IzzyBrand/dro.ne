class Database:
    HOST = "localhost"
    USER = "root"
    PWD_ENV_VAR = "DRONE_DB_PWD"  # environ variable
    DB_NAME = "dronedb"


""" General timing constants """
class Timing:
    UPDATE_INTERVAL = 1   # seconds