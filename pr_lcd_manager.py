#!/usr/bin/python

import i2c_lcd_driver as lcd
import time

from threading import Thread

class lcd_manager:
    mylcd = None            # LCD driver
    lcd_t = None            # LCD controller thread
    volume = ""             # Volume level (string), set externally via set_info() interface
    title = ""              # Current song title, set externally via set_info() interface
    stream_title = ""       # Current playing media source title, set externally via set_info() interface
    mytime_mgr = None       # Object that provides datetime preformated strings
    mode = "clock"          # Current display mode

    #Loop variables
    my_title = ""           # Song title being displayed in LCD
    my_stream_title = ""    # Media source title being displayed in LCD
    my_volume = ""          # Volume level being displayed in LCD

    # Interface for player to provide information
    def info_set(self, info, value):
        if info == "title":
            self.title = value
        elif info == "stream_title":
            self.stream_title = value
        elif info == "volume":
            self.volume = value

    def __init__(self, time_mgr):
        self.mylcd = lcd.lcd()
        self.mytime_mgr = time_mgr

    def start_lcd_controller(self):
        self.lcd_t = Thread(target = self.loop, args =())
        self.lcd_t.start()

    def set_mode(self, mode):
        if self.mode == mode:
            return

        self.mode = mode

        if self.mode == "clock":
            self.title = ""
            self.stream_title = ""
            self.my_title = ""
            self.my_stream_title = ""
            self.mytime_mgr.reset()

        if self.mode == "alarm":
            self.title = "ALARM"
            self.stream_title = "00:00"
            self.my_title = ""
            self.my_stream_title = ""

    # Thread to constantly update the LCD
    # The LCD will update every second in clock mode and
    # twice a second in playback mode. Lots of room for
    # improvement here
    def loop(self):
        v_cnt = -1
        t_len = 0
        t_cnt = 0
        new_title = True

        counter = 0
        tm = ""
        dt = ""

        while True:
            if self.mode == "player":
                if self.my_title != self.title:
                    self.my_title = self.title
                    t_cnt = 0
                    t_len = len(self.my_title)
                    new_title = True

                # When a new volume level is set, the volume will be displayed
                # in the lower line of the LCD for 2 loops (tracked via v_cnt)
                if self.my_volume != self.volume:
                    self.my_volume = self.volume
                    v_cnt = 2

                if v_cnt > 0:
                    self.mylcd.lcd_display_string(self.my_volume.center(16), 2, 0)
                    v_cnt -= 1
                elif v_cnt == 0:
                    self.mylcd.lcd_display_string(self.my_stream_title.center(16), 2, 0)
                    v_cnt -= 1
                else:
                    # If we are not displaying the volume level, check if we need to
                    # update the media title
                    if self.stream_title != self.my_stream_title:
                        self.my_stream_title = self.stream_title
                        self.mylcd.lcd_display_string(self.my_stream_title.center(16), 2, 0)

                # Display and/or rotate the song title on the first LCD line (if necessary)
                if t_len <= 16:
                    if new_title:
                        disp_title = self.my_title.center(16)
                        self.mylcd.lcd_display_string(disp_title, 1, 0)
                else:
                    disp_title = ((self.my_title + " # ")[t_cnt:] + (self.my_title + " # ")[:t_cnt])[:16]
                    self.mylcd.lcd_display_string(disp_title, 1, 0)
                    t_cnt = (t_cnt + 1) % (t_len + 3)

                time.sleep(0.5)
            elif self.mode == "clock":
                # Get new date/time from the datetime provider
                # Date will of course change every 24H, but the time
                # changes every second due to the ":" character blinking
                # TODO: some optimization needed here
                dt = self.mytime_mgr.get_date()
                tm = self.mytime_mgr.get_time()

                if dt != None:
                    self.mylcd.lcd_display_string(dt, 1, 0)
                if tm != None:
                    self.mylcd.lcd_display_string(tm, 2, 0)

            elif self.mode == "alarm":
                pass

                time.sleep(1)
