# Check for an internet connection, and if we find one, broadcast the current 
# IP address (via push notification using PushSafer service). Otherwise, we
# reboot the Raspberry Pi in access point mode.

import os
import netifaces as ni
import socket
import ConfigParser

from subprocess import call
from pushsafer import init, Client

# Path to bash file to restart Pi into access point mode.
RESTART_AP_BASH_PATH = "../toggle_wifi_access_point/restart_access_point"

# Define internet adapter so that we can find our external IP address.
ADAPTER = "wlan0"
# ADAPTER = u"{7E33E52A-7BBD-4480-8B1E-BAFC69B2C26D}"

# Parse client keys from pushsafer.keys configuration file.
pushsafer_cfg = ConfigParser.ConfigParser()
pushsafer_cfg.read("pushsafer.keys")
keys = pushsafer_cfg.get("PushSafer", "keys")
keys.replace(" ", "")   # remove any and all spaces
keys = keys.split(",")  # convert string to list

# Return True if there is an active internet connection.
def internet_connection(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)

    Function source from:
    https://stackoverflow.com/questions/3764291/checking-network-connection/33117579#33117579
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as ex:
        print ex.message
        return False

# Push IP address to phone as notification. This function sends 'message' to 
# all IP addresses specified in the 'keys' list. It uses the PushSafer
# python module for push functionality.
def push(title="", message="", keys=None):
    if keys is not None:
        for key in keys:
            init(key)
            Client("").send_message(message, title, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            print "Pushed notification!"


if __name__ == "__main__":
    # Check if internet connection exists.
    if internet_connection():
        print "Internet connection established."
        # Since we have internet access, let's find out our IP address.
        ni.ifaddresses(ADAPTER)
        ip = ni.ifaddresses(ADAPTER)[ni.AF_INET][0]["addr"]
        print "My IP address is %s." % ip
        # Now, broadcast the IP.
        push("Raspberry Pi IP Address", "IP address is %s." % ip, keys)
    else:
        print "Failed to establish internet connection."
        # Since we don't have internet connection, reboot Pi as access point.
        print "Rebooting system as access point."
        call([RESTART_AP_BASH_PATH])