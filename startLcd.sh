#!/bin/bash
sleep 30 
/usr/bin/python3.5 /home/pi/sign/lcdSign.py > /var/log/lcdSign.log 2>&1 &
