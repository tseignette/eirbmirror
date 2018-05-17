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
from threading import Event, Thread


def update_temp():
    global temperature
    global humidity
    temperature_tmp, humidity_tmp = Adafruit_DHT.read_retry(sensor, pin) # updating temparature and humidity
    temperature = temperature_tmp
    humidity = humidity_tmp

class TemperatureThread(Thread):
    def __init__(self):
        ''' Constructor. '''
        Thread.__init__(self)
        update_temp()
 
    def run(self):
        while True:
            time.sleep(4)
            update_temp()
        # for i in range(1, self.val):
        #     print('Value %d in thread %s' % (i, self.getName()))
 
        #     # Sleep for random time between 1 ~ 3 second
        #     secondsToSleep = randint(1, 5)
        #     print('%s sleeping fo %d seconds...' % (self.getName(), secondsToSleep))
        #     time.sleep(secondsToSleep)


# thread
def call_repeatedly(interval, func, *args):
  stopped = Event()
  def loop():
      while not stopped.wait(interval): # the first call is in `interval` secs
          func(*args)
  Thread(target=loop).start()
  return stopped.set

  # global
temperature = 0
humidity = 0


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

    # thread
    # update_temp()
    myThreadOb1 = TemperatureThread()
    myThreadOb1.setName('Thread temperature')
 
    # Start running the threads!
    myThreadOb1.start()
    # call_repeatedly(2, update_temp)
    # threading.Timer(2.0, update_temp).start()

    try:
        # Wait indefinitely until the user terminates the script
        while True:
            time.sleep(1)
            date = datetime.datetime.now() # updating time and date

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
