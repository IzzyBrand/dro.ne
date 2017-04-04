#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
© Copyright 2015-2016, 3D Robotics.
mission_import_export.py: 

Documentation is provided at http://python.dronekit.io/examples/mission_import_export.html

This contains all the commands to handle uploading a mission to the autopilot from a file
"""

from dronekit import connect, Command
import time


def read(vehicle, missionFile):
    """
    Load a mission from a file into a list. The mission definition is in the Waypoint file
    format (http://qgroundcontrol.org/mavlink/waypoint_protocol#waypoint_file_format).

    This function is used by upload_mission().
    """
    cmds = vehicle.commands
    missionlist=[]
    f = open(missionFile)
    for i, line in enumerate(f):
        if i==0:
            if not line.startswith('QGC WPL 110'):
                raise Exception('File is not supported WP version')
        else:
            linearray=line.split('\t')
            ln_index=int(linearray[0])
            ln_currentwp=int(linearray[1])
            ln_frame=int(linearray[2])
            ln_command=int(linearray[3])
            ln_param1=float(linearray[4])
            ln_param2=float(linearray[5])
            ln_param3=float(linearray[6])
            ln_param4=float(linearray[7])
            ln_param5=float(linearray[8])
            ln_param6=float(linearray[9])
            ln_param7=float(linearray[10])
            ln_autocontinue=int(linearray[11].strip())
            cmd = Command( 0, 0, 0, ln_frame, ln_command, ln_currentwp, ln_autocontinue, 
                ln_param1, ln_param2, ln_param3, ln_param4, ln_param5, ln_param6, ln_param7)
            missionlist.append(cmd)
    f.close()
    return missionlist


def upload(vehicle, missionFile):
    """
    Upload a mission from a file. 
    """
    #Read mission from file
    print '[UPLOAD]',
    missionlist = read(vehicle, missionFile)
    #Clear existing mission from vehicle
    print ' - read from', missionFile,
    cmds = vehicle.commands
    cmds.clear()
    print ' - clear',
    #Add new mission to vehicle
    for command in missionlist:
        cmds.add(command)
    vehicle.commands.upload()
    print ' - upload'
    return missionlist


def download(vehicle):
    """
    Downloads the current mission and returns it in a list.
    It is used in save_mission() to get the file information to save.
    """
    print " Download mission from vehicle"
    missionlist=[]
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()
    for cmd in cmds:
        missionlist.append(cmd)
    return missionlist


def upload_and_verify(vehicle, missionFile):
    uploaded_mission = upload(vehicle, missionFile)
    downloaded_mission = download(vehicle)
    print uploaded_mission
    print downloaded_mission
    return uploaded_mission == downloaded_mission


