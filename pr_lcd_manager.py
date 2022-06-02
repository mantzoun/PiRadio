#!/usr/bin/python

import i2c_lcd_driver as lcd
import time

from threading import Thread

class lcd_manager:
    mylcd = None
    lcd_t = None
    volume = ""
    title = ""
    stream_title = ""
    mytime_mgr = None
    mode = "clock"
    v_cnt = -1

    #Loop variables
    my_title = ""
    my_stream_title = ""
    my_volume = ""

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
        self.mode = mode

        if self.mode == "clock":
            self.title = ""
            self.stream_title = ""
            self.my_title = ""
            self.my_stream_title = ""
            self.mytime_mgr.reset()

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
                    if self.stream_title != self.my_stream_title:
                        self.my_stream_title = self.stream_title
                        self.mylcd.lcd_display_string(self.my_stream_title.center(16), 2, 0)

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
                dt = self.mytime_mgr.get_date()
                tm = self.mytime_mgr.get_time()

                if dt != None:
                    self.mylcd.lcd_display_string(dt, 1, 0)
                if tm != None:
                    self.mylcd.lcd_display_string(tm, 2, 0)

                time.sleep(1)
