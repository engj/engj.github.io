#!/bin/bash

sudo ifconfig wlan0 down
sudo killall nm-applet
sudo killall wpa_supplicant
sleep .1

for (( i=1; i<=10; i++ ))
do
  sleep .17
  sudo killall wpa_supplicant
done

sudo ifconfig wlan0 up 192.168.1.1 netmask 255.255.255.0

echo "Configuration done, running hostapd."

sudo hostapd -d /etc/hostapd/hostapd.conf

echo "hostapd down, restoring nm-applet"

nm-applet &

