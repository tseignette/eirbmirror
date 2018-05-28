#!/usr/bin/env python
#-*- coding: utf-8 -*-

import Adafruit_DHT
import config
import cv2
import datetime
from detect_night import *
import numpy as np
import picamera
import picamera.array
from PIL import Image
import RPi.GPIO as GPIO
from screeninfo import get_monitors
import time


# ==================================================================================================
# SETUP
# ==================================================================================================

# date and time format, font
format = '%d/%m/%Y %H:%M'
font = cv2.FONT_HERSHEY_DUPLEX

# temperature and humidity
sensor = Adafruit_DHT.DHT11
pin = 26
temp_count = 0

# get screen size
monitor = get_monitors()[0]
width = monitor.width
height = monitor.height
# width = monitor.width
# height = monitor.height
overlay_width = monitor.width
overlay_height = 64
overlay_fullscreen = False
overlay_window = (0, 0, overlay_width, overlay_height)
framerate = 60


# ==================================================================================================
# MAIN LOOP
# ==================================================================================================

with picamera.PiCamera() as camera:
    # starting camera
    camera.resolution = (height, width)
    camera.framerate = framerate
    camera.start_preview(rotation=90, layer=0)

    # night detection
    night_detect = NightDetectionThread(camera, width, height)
    night_detect.start()

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
            date = datetime.datetime.now() # updating time and date

            # adding date and time to img
            img = np.zeros((overlay_height, overlay_width, 3), dtype=np.uint8)
            temperature, humidity = Adafruit_DHT.read_retry(sensor, pin) # updating temparature and humidity
            cv2.putText(
                img,
                date.strftime(format)
                    + ' Temperature : {0:0.1f}*C'.format(temperature)
                    + ' Humidity : {0:0.1f}%'.format(humidity),
                (20, overlay_height/2 + 5),
                font,
                1,
                (255, 255, 255)
            )

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

            time.sleep(8)

    finally:
        camera.remove_overlay(old_overlay)
        camera.remove_overlay(new_overlay)
