#!/usr/bin/env python
#-*- coding: utf-8 -*-

import time
import numpy as np
import cv2
import picamera
import picamera.array
from threading import Event, Thread
import RPi.GPIO as GPIO

DAY_MODE = 0
NIGHT_MODE = 1


class NightDetectionThread(Thread):

    def __init__(self, picamera, width=1920, height=1080, gpio_led=13, threshold_day=30, threshold_night=200):
        Thread.__init__(self)
        self.interval_day = 5
        self.interval_night = 1
        self.mode = DAY_MODE
        self.picamera = picamera
        self.width = width
        self.height = height
        self.img_captured = np.empty((height * width * 3,), dtype=np.uint8)
        self.img_gray = np.empty((height, width, 3), dtype=np.uint8)
        self.gpio_led = gpio_led
        self.threshold_day = threshold_day
        self.threshold_night = threshold_night
        """
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(gpio_led, GPIO.OUT, initial=GPIO.LOW)
        """
    
    def isNight(self):
        return self.mode == NIGHT_MODE

    def run(self):
        while True:
            self.picamera.capture(self.img_captured, "rgb")
            output = self.img_captured.reshape(((self.height, self.width, 3)))
            cv2.cvtColor(output, self.img_gray, cv2.COLOR_RGB2GRAY)
            mean = np.mean(self.img_gray)
            print ("mean : " + mean)
            """
            if self.mode == DAY_MODE:
                self.picamera.capture(self.img_captured, "rgb")
                cv2.cvtColor(self.img_captured, self.img_gray, cv2.COLOR_RGB2GRAY)
                mean = np.mean(self.img_gray)
                if mean < self.threshold_day:
                    GPIO.output(self.gpio_led, GPIO.HIGH)
                    self.mode = NIGHT_MODE
                
            elif self.mode == NIGHT_MODE:
                self.picamera.capture(self.img_captured, "rgb")
                cvtColor(self.img_captured, self.img_gray, cv2.COLOR_RGB2GRAY)
                mean = np.mean(self.img_gray)
                if mean > self.threshold_night:
                    GPIO.output(self.gpio_led, GPIO.LOW)
                    self.mode = DAY_MODE
            """
            if self.mode == DAY_MODE:
                time.sleep(self.interval_day)
            elif self.mode == NIGHT_MODE:
                time.sleep(self.interval_night)
            
            