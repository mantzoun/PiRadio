#!/usr/bin/python

import subprocess
import signal
import os
import re
import time
import string
import RPi.GPIO as GPIO

from threading import Thread

from pr_time_manager import time_manager
from pr_lcd_manager import lcd_manager
from pr_mplayer_wrapper import mplayer_wrapper
from pr_sources import sources

class Main:
    last_stream = 0
    player = None
    lcd_mgr = None

    b1_push_time = 0
    b2_push_time = 0

    def gpio_init(self):
        init_done = False

        while not init_done:
            # When running immediately after boot (e.g. via cron), GPIO initialization
            # will fail, so this may take a couple of tries
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)

                GPIO.add_event_detect(4, GPIO.BOTH,     callback = self.button1_cb, bouncetime=50)
                GPIO.add_event_detect(8, GPIO.BOTH,     callback = self.button2_cb, bouncetime=50)
                GPIO.add_event_detect(7, GPIO.FALLING,  callback = self.button3_cb, bouncetime=250)
                GPIO.add_event_detect(25, GPIO.FALLING, callback = self.button4_cb, bouncetime=250)

                init_done = True
            except:
                print("*** GPIO init failed, retrying...")
                time.sleep(2)

    # Button 1
    # Volume down on sort press, previous track on long press
    # TODO: use to set alarm clock
    def button1_cb(self, channel):
        if self.player.on():
            time.sleep(.01)
            if GPIO.input(channel):
                if (time.time()) > (0.3 + self.b1_push):
                    self.player.prev_track()
                else:
                    self.player.vol_down()
            else:
                self.b1_push = time.time()

    # Button 2
    # Volume up on sort press, next track on long press
    # TODO: use to set alarm clock
    def button2_cb(self, channel):
        if self.player.on():
            time.sleep(.01)
            if GPIO.input(channel):
                if (time.time()) > (0.3 + self.b2_push):
                    self.player.next_track()
                else:
                    self.player.vol_up()
            else:
                self.b2_push = time.time()

    # Button 3
    # Play next configured source
    # TODO: Switch to alarm configuration
    def button3_cb(self, channel):
        if self.player.on():
            self.last_stream = (self.last_stream + 1) % len(sources)

            self.player.stop()
            self.player.start(sources[self.last_stream][0], sources[self.last_stream][1], sources[self.last_stream][2])

    # Button 4
    # Start / Stop media playback
    def button4_cb(self,channel):
        if self.player.on():
            self.player.stop()
            self.lcd_mgr.set_mode("clock")
        else:
            self.player.start(sources[self.last_stream][0], sources[self.last_stream][1], sources[self.last_stream][2])
            self.lcd_mgr.set_mode("player")

    # Try to exit gracefully when signalled
    def handler(self, signum, frame):
        print("*** Exiting")
        print("*** GPIO cleanup")
        GPIO.cleanup()

        if self.player.on():
            print("*** Stopping Stream")
            self.player.stop()

        exit(0)

    def run(self):
        signal.signal(signal.SIGINT, self.handler)

        print("*** Startup")

        print("*** Setup GPIOs")
        self.gpio_init()

        time_mgr = time_manager()

        print("*** Init LCD")
        self.lcd_mgr = lcd_manager(time_mgr)
        self.lcd_mgr.start_lcd_controller()

        self.player = mplayer_wrapper(self.lcd_mgr.info_set)

        while True:
            time.sleep(100000)

if __name__ == "__main__":
    main = Main()
    main.run()
