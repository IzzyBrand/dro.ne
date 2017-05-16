# RASPI SETUP

## RASPI-CONFIG
- enable ssh
- disable serial
- expand os
- disable gui
- set hostname to droneberry
- set password to *********
- reboot

## DEPENDENCIES
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install vim python-pip python-dev libxml2-dev libxslt-dev
sudo pip install requests monotonic future mavproxy dronekit pyserial pymavlink 
```

## DRONEKIT
Dronekit was edited according to ticket 585 to avoid receiving problematic messages from a GCS
```
sudo mv /usr/lib/python2.7/site-packages/dronekit/test/__init.py__ /usr/lib/python2.7/site-packages/dronekit/test/__init.py__.original
sudo cp ~/dro.ne/droneberry/dronekit_util/__init.py /usr/lib/python2.7/site-packages/dronekit/test/__init.py__
```

## Set up 3G LTE connectivity on Pi
- http://www.instructables.com/id/Raspberry-Pi-as-a-3g-Huawei-E303-wireless-Edima/
- http://apn-settings.com/t-mobile-apn-settings-step-by-step-configuration/
- 'connect' bash script can be found in '/umtskeeper'