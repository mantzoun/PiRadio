import i2c_lcd_driver as lcd
import time

from threading import Thread

class lcd_manager:
    mylcd = None            # LCD driver
    lcd_t = None            # LCD controller thread
    volume = ""             # Volume level (string), set externally via set_info() interface
    line1 = ""              # Current song title, set externally via info_set() interface
                            # Or date, in clock mode, alarm title in alarm mode etc.
    line2 = ""              # Current playing media source title, set externally via set_info() interface
                            # Or time, in clock mode, alatm time in alarm mode, etc.
    mytime_mgr = None       # Object that provides datetime preformated strings
    mode = "clock"          # Current display mode

    #Loop variables
    my_line1 = ""           # line1 being displayed in LCD
    my_line2 = ""           # line2 title being displayed in LCD
    my_volume = ""          # Volume level being displayed in LCD

    keep_alive = True

    # Interface for player to provide information
    def info_set(self, value1, value2):
        #TODO use another keyword for volume
        if value1 == "volume":
            self.volume = value
        else:
            if value1 != None:
                self.line1 = value1
            if value2 != None:
                self.line2 = value2

    def __init__(self, time_mgr):
        self.mylcd = lcd.lcd()
        self.mytime_mgr = time_mgr

    def terminate(self):
        self.keep_alive = False

    def start_lcd_controller(self):
        self.lcd_t = Thread(target = self.loop, args =())
        self.lcd_t.start()

    def set_mode(self, mode):
        if self.mode == mode:
            return

        self.mode = mode

        if self.mode == "clock":
            self.line1 = ""
            self.line2 = ""
            self.my_line1 = ""
            self.my_line2 = ""
            self.mytime_mgr.reset()

        if self.mode == "alarm":
            self.line1 = "ALARM"
            self.line2 = "00:00"
            self.my_line1 = ""
            self.my_line2 = ""

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

        while self.keep_alive:
            if self.mode == "player":
                if self.my_line1 != self.line1:
                    self.my_line1 = self.line1
                    t_cnt = 0
                    t_len = len(self.my_line1)
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
                    self.mylcd.lcd_display_string(self.my_line2.center(16), 2, 0)
                    v_cnt -= 1
                else:
                    # If we are not displaying the volume level, check if we need to
                    # update the media title
                    if self.line2 != self.my_line2:
                        self.my_line2 = self.line2
                        self.mylcd.lcd_display_string(self.my_line2.center(16), 2, 0)

                # Display and/or rotate the song title on the first LCD line (if necessary)
                if t_len <= 16:
                    if new_title:
                        disp_title = self.my_line1.center(16)
                        self.mylcd.lcd_display_string(disp_title, 1, 0)
                else:
                    disp_title = ((self.my_line1 + " # ")[t_cnt:] + (self.my_line1 + " # ")[:t_cnt])[:16]
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

                time.sleep(1)
            elif self.mode == "alarm":
                self.mylcd.lcd_display_string(self.line1.center(16), 1, 0)
                self.mylcd.lcd_display_string(self.line2.center(16), 2, 0)

                time.sleep(0.5)
