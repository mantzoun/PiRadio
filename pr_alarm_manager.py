import time

from pr_sources import sources

class alarm_manager:
    alarm_list = []
    alarm_index = -1

    info_set = None
    alarm_cb = None

    days = ["m", "t", "w", "t", "f", "s", "s"]
    DAYS = ["M", "T", "W", "T", "F", "S", "S"]

    #cancel alarm variables
    alarm_cancel = False
    pointers = [ [" * ", "   "],
                 ["   ", " * "] ]
    pointer_pos = 0

    #new alarm variables
    new_alarm = False
    new_alarm_menu_lvl = 0
    new_hour    = 0
    new_min     = 0
    new_repeat  = 0b0000000
    new_stream  = 0
    new_repeat_pos = 0

    def __init__(self, info_set, alarm_cb):
        self.info_set = info_set
        self.alarm_cb = alarm_cb

        try:
            with open('alarms.txt', 'r') as file:
                for line in file:
                    alarm = self.parse_alarm(line)
                    if alarm != -1:
                        self.alarm_list.append(alarm)
        except:
            print("no alarms file present")

    def get_repeat_string(self, repeat_map, pointer):
        res = ""
        for i in range(0, 7):
            if i == pointer:
                res += "*"
            else:
                res += " "
            if repeat_map & (1 << i) > 0:
                res += self.DAYS[i]
            else:
                res += self.days[i]
        return res

    def parse_alarm(self, alarm_line):
        alarm_info = alarm_line.split(",")
        if len(alarm_info) != 4:
            print("error alarm " + alarm_info)
            return -1
        return alarm_info

    def show_new_alarm_menu(self):
        if self.new_alarm_menu_lvl == 0:
            self.info_set("title", "New Alarm ")
            self.info_set("stream_title", "%02d:%02d" %(self.new_hour, self.new_min))
        if self.new_alarm_menu_lvl == 1:
            self.info_set("title", "Repeat?")
            self.info_set("stream_title", self.get_repeat_string(self.new_repeat, self.new_repeat_pos))
        if self.new_alarm_menu_lvl == 2:
            self.info_set("title", "Playback source")
            self.info_set("stream_title", sources[self.new_stream][1])
        if self.new_alarm_menu_lvl == 3:
            self.info_set("title", "Alarm set")
            self.info_set("stream_title", "")
            #save alarm info here
            self.new_alarm = False
            self.alarm_index = -1
            self.new_hour = 0
            self.new_min = 0
            self.new_repeat = 0
            self.new_stream = 0
            self.new_repeat_pos = 0
            self.new_alarm_menu_lvl = 0

            time.sleep(1)
            self.show_alarm_info()

    # show alarm info
    # Cycle through alarms with button 3
    # Cycle through alarm fields with button 4
    # Modify alarm fields with keys 1/2
    # return -1 after last alarm in list, to return to clock mode
    def show_alarm_info(self):
        if self.new_alarm == True:
            # exit alarm_mode
            self.new_alarm = False
            self.alarm_index = -1
            return -1

        if self.alarm_index == -1:
            self.alarm_index = 0
        else:
            self.alarm_index += 1

        if self.alarm_index == len(self.alarm_list):
            # go into new alarm mode
            self.new_alarm_menu_lvl = 0
            self.new_alarm = True
            self.new_hour = 0
            self.new_min = 0
            self.new_repeat = 0
            self.new_stream = 0
            self.new_repeat_pos = 0
            self.show_new_alarm_menu()
        else:
            alarm = self.alarm_list[self.alarm_index]
            self.info_set("title", "Alarm " + str(self.alarm_index))
            self.info_set("stream_title", alarm[0] + ":" + alarm[1])

            return 0

    def show_cancel_alarm_confirmation(self):
        self.info_set("stream_title", self.pointers[self.pointer_pos][0] + "No / Yes" +
                                      self.pointers[self.pointer_pos][1])

    def button1(self):
        if self.alarm_cancel == True:
            self.pointer_pos = (self.pointer_pos + 1) % 2
            self.show_cancel_alarm_confirmation()
        elif self.new_alarm == True:
            if self.new_alarm_menu_lvl == 0:
                self.new_hour = (self.new_hour + 1) % 24
            elif self.new_alarm_menu_lvl == 1:
                self.new_repeat_pos = (self.new_repeat_pos + 1 ) % 7
            elif self.new_alarm_menu_lvl == 2:
                self.new_stream -= 1
                if self.new_stream < 0:
                    self.new_stream = len(sources) - 1

            self.show_new_alarm_menu()

    def button2(self):
        if self.alarm_cancel == True:
            self.pointer_pos = (self.pointer_pos + 1) % 2
            self.show_cancel_alarm_confirmation()
        elif self.new_alarm == True:
            if self.new_alarm_menu_lvl == 0:
                self.new_min = (self.new_min + 5) % 60
            elif self.new_alarm_menu_lvl == 1:
                self.new_repeat = self.new_repeat ^ (1 << self.new_repeat_pos)
            elif self.new_alarm_menu_lvl == 2:
                self.new_stream = (self.new_stream + 1) % len(sources)

            self.show_new_alarm_menu()

    def button3(self):
        if self.alarm_cancel == True:
            return 0
        else:
            return self.show_alarm_info()

    # Show Cancel Alarm menu when in display info mode
    # Advance to next config menu in new alarm mode
    def button4(self):
        if self.new_alarm == True:
            self.new_alarm_menu_lvl += 1
            self.show_new_alarm_menu()
        else:
            if self.alarm_cancel == True:
                if self.pointer_pos == 1:
                    #confirmed
                    print("Alarm canceled")
                    self.alarm_cancel = False
                    self.show_alarm_info()
                else:
                    #go back
                    self.alarm_cancel = False
                    self.show_alarm_info()
            else:
                self.info_set("title", "Clear Alarm " + str(self.alarm_index) + " ?")
                self.show_cancel_alarm_confirmation()
                self.alarm_cancel = True
