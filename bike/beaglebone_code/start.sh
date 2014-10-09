#!/bin/bash

sleep 13

killall node
killall node4

ifconfig eth0 down
ifconfig wlan0 up 192.168.1.2 netmask 255.255.255.0

sleep .1

iwconfig wlan0 mode managed essid winning

sleep .1

sleep 1
python /home/root/br/pycodes/server.py &
killall node4


echo uart2pinmux > /sys/devices/bone_capemgr.9/slots
