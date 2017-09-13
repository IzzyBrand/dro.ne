# dro.ne

## droneberry
Contains the onboard Raspberry PI Python code for each drone.

## dronesvr
Contains webserver code for both front and back-end database communication.

## dronemgr
Contains back-end state machine code for managing and delegating drones in realtime.

# Notes

Connect FONA following this tutorial: https://github.com/initialstate/fona-raspberry-pi-3/wik

# Luna TODO list

- reach out to PVDonuts or something else... decide what we're dropping (?)
- get drone working + put hours on it so we trust it
- refactor API (?)
- throw out state controller v2, use v1 for demo purposes
- go through codebase and check that everything works properly
- assemble gripper and test
- think of state controller v3 design so that states and flows can be easily defined and interpreted
- what does drone handle? what does back-end handle?
- store missions in cloud (i.e. lunadrop.com/missions/a_to_b.wp and download them to the drone if they're not already stored locally from a previous download
- camera assisted landing
- go through front-end UI code and verify that it all works
- add PAUSE to administrator UI (?)

