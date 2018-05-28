#!/usr/bin/env python
#-*- coding: utf-8 -*-

import time
import numpy as np
import cv2
import io
import picamera
import picamera.array
from threading import Event, Thread

import RPi.GPIO as GPIO

DAY_MODE = 0
NIGHT_MODE = 1

class NightDetectionThread(Thread):

    def __init__(self, camera, width=1920, height=1080, gpio_led=19, threshold=50):
        Thread.__init__(self)
        self.interval_day = 1
        self.interval_night = 30
        self.mode = DAY_MODE
        self.camera = camera
        self.width = width
        self.height = height
        self.img_captured = np.empty((height * width * 3), dtype=np.uint8)
        self.img_gray = np.empty((height, width, 1), dtype=np.uint8)
        self.gpio_led = gpio_led
        self.threshold = threshold
        self.mean = 0
        self.overlay = None
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(gpio_led, GPIO.OUT)
        self.turnIrLedOff()
        self.switchToDay()

    def turnIrLedOn(self):
        GPIO.output(self.gpio_led, True)

    def turnIrLedOff(self):
        GPIO.output(self.gpio_led, False)

    def switchToDay(self):
        self.turnIrLedOff()
        self.mode = DAY_MODE
        self.overlay = self.camera.add_overlay(
            np.zeros((self.width, self.height, 3), dtype=np.uint8),
            layer=1,
            alpha=255,
            size=(self.width, self.height)
        )

    def switchToNight(self):
        self.turnIrLedOn()
        self.mode = NIGHT_MODE
        self.camera.remove_overlay(self.overlay)
    
    def isNight(self):
        return self.mode == NIGHT_MODE

    def get_mean(self):
        return self.mean

    def run(self):
        while True:
            with picamera.array.PiRGBArray(self.camera) as stream:
                if(self.mode == NIGHT_MODE):
                    self.turnIrLedOff()

                self.camera.capture(stream, "bgr")
                self.img_captured = stream.array
                self.img_gray = cv2.cvtColor(self.img_captured, cv2.COLOR_BGR2GRAY)
                self.mean = np.mean(self.img_gray)

                if(self.mode == NIGHT_MODE):
                    self.turnIrLedOn()

                if self.mode == DAY_MODE:
                    if self.mean < self.threshold:
                        self.switchToNight()
                    else:
                        time.sleep(self.interval_day)
                    
                elif self.mode == NIGHT_MODE:
                    if self.mean > self.threshold:
                        self.switchToDay()
                    else:
                        time.sleep(self.interval_night)
            
            
