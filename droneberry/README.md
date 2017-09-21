# droneberry

Python code onboard each drone, implemented on Raspberry PIs.

## Setting Up Internet Access (via LTE) ##

(Fona Wiki)[https://github.com/initialstate/fona-raspberry-pi-3/wiki]

## Configuring Access Point and Client modes for Pi ##

(Lewis Cowles's Github Gist)[https://gist.github.com/Lewiscowles1986/fecd4de0b45b2029c390]

### Scripts to toggle Access Point and Client modes ###

restart_client
```
    cp dhcpcd.conf.client /etc/dhcpcd.conf
    cp interfaces.client /etc/network/interfaces
    systemctl disable hostapd
    shutdown -r now
```

restart_access_point
```
    cp dhcpcd.conf.access_point /etc/dhcpcd.conf
    cp interfaces.access_point /etc/network/interfaces
    systemctl enable hostapd
    shutdown -r now
```
