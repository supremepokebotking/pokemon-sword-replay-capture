#!/usr/bin/env python3
import argparse
import serial
from time import sleep

#parser = argparse.ArgumentParser()
#parser.add_argument('port', default='/dev/tty.usbserial-A50285BI')
#args = parser.parse_args()

def send(msg, duration=0.1):
    print(msg)
    ser.write(f'{msg}\r\n'.encode('utf-8'));
    sleep(duration)
    ser.write(b'RELEASE\r\n');
#/dev/tty.usbserial-A50285BI
#ser = serial.Serial('/dev/tty.usbserial-A50285BI', 9600)
#ser = serial.Serial('/dev/tty.usbserial-AI05M0GQ', 9600)
ser = serial.Serial('/dev/tty.usbserial-AQ00LCW6', 9600)
#ser = serial.Serial(args.port, 9600)
