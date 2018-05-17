#!/usr/bin/env python
#-*- coding: utf-8 -*-

import datetime
import time
import numpy as np
import cv2
from screeninfo import get_monitors
import picamera
import picamera.array
from PIL import Image
import Adafruit_DHT


# date and time
date = datetime.datetime.now()
format = "%d/%m/%Y %H:%M:%S"
font = cv2.FONT_HERSHEY_SIMPLEX

# temperature and humidity
sensor = Adafruit_DHT.DHT11
pin = 26
temp_count = 0

# get screen size
monitor = get_monitors()[0]
width = 1600
height = 900
overlay_width = monitor.width
overlay_height = 64
overlay_fullscreen = False
overlay_window = (0, 0, overlay_width, overlay_height)
framerate = 60


# main loop
with picamera.PiCamera() as camera:
    # starting camera
    camera.resolution = (width, height)
    camera.framerate = framerate
    camera.start_preview()

    # adding first overlay
    img = np.zeros((overlay_height, overlay_width, 3), dtype=np.uint8)

    old_overlay = camera.add_overlay(np.getbuffer(img), layer=3, alpha=255, size=(overlay_width, overlay_height))
    old_overlay.fullscreen = overlay_fullscreen
    old_overlay.window = overlay_window

    new_overlay = camera.add_overlay(np.getbuffer(img), layer=3, alpha=255, size=(overlay_width, overlay_height))
    new_overlay.fullscreen = overlay_fullscreen
    new_overlay.window = overlay_window

    try:
        # Wait indefinitely until the user terminates the script
        while True:
            time.sleep(1)
            date = datetime.datetime.now() # updating time and date
            if(temp_count % 5 == 0):
                temp_count = 0
                humidity, temperature = Adafruit_DHT.read_retry(sensor, pin) # updating temparature and humidity
            temp_count += 1;

            # adding date and time to img
            img = np.zeros((overlay_height, overlay_width, 3), dtype=np.uint8)
            cv2.putText(
                img,
                date.strftime(format) + ' Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity),
                (20,overlay_height/2 + 5),
                font,
                1,
                (255, 255, 255))

            new_overlay = camera.add_overlay(
                np.getbuffer(img),
                layer=3, alpha=255,
                size=(overlay_width, overlay_height),
                fullscreen=overlay_fullscreen,
                window=overlay_window
            )
            camera.remove_overlay(old_overlay)

            # swapping new overlay with old
            tmp = old_overlay
            old_overlay = new_overlay
            new_overlay = old_overlay


    finally:
        camera.remove_overlay(old_overlay)
        camera.remove_overlay(new_overlay)
