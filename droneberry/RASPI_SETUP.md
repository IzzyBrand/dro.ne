# RASPI SETUP

## RASPI-CONFIG
- enable ssh
- disable serial
- expand os
- disable gui
- set hostname to droneberry
- set password to *********
- reboot

## MacOS
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install vim python-pip python-dev libxml2-dev libxslt-dev
sudo pip install monotonic future mavproxy dronekit pyserial pymavlink 
```

## Set up 3G LTE connectivity on Pi
- http://www.instructables.com/id/Raspberry-Pi-as-a-3g-Huawei-E303-wireless-Edima/
- http://apn-settings.com/t-mobile-apn-settings-step-by-step-configuration/
- 'connect' bash script can be found in '/umtskeeper'