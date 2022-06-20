import time

from pr_sources import sources

class Alarm:
    repeat  = 0
    hours   = 0
    minutes = 0
    source  = 0

    def __init__(self, alarm_info = [0, 0, 0, 0]):
        self.hours   = alarm_info[0]
        self.minutes = alarm_info[1]
        self.repeat  = alarm_info[2]
        self.source  = alarm_info[3]

class alarm_manager:
    alarms_file = 'alarms.txt'

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
    new_alarm = None
    new_alarm_menu_lvl = 0
    new_repeat_pos = 0

    def __init__(self, info_set, alarm_cb):
        self.info_set = info_set
        self.alarm_cb = alarm_cb

        try:
            with open(self.alarms_file, 'r') as file:
                for line in file:
                    alarm = self.parse_alarm(line)
                    if alarm != -1:
                        self.alarm_list.append(alarm)
        except:
            print("no alarms file present")

    def write_alarm_file(self):
       # try:
            with open(self.alarms_file, 'w') as file:
                for alarm in self.alarm_list:
                    file.write("%d, %d, %d, %d\n" % (alarm.hours,
                                                     alarm.minutes,
                                                     alarm.repeat,
                                                     alarm.source))
       # except:
       #     print("Error saving alarms")

    def get_repeat_string(self, repeat_map, pointer = None):
        res = ""
        for i in range(0, 7):
            if pointer != None:
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

        alarm = Alarm([int(i) for i in alarm_info])

        return alarm

    def show_new_alarm_menu(self):
        if self.new_alarm_menu_lvl == 0:
            self.info_set("New Alarm", "%02d:%02d" %(self.new_alarm.hours, self.new_alarm.minutes))
        if self.new_alarm_menu_lvl == 1:
            self.info_set("Repeat?", self.get_repeat_string(self.new_alarm.repeat, self.new_repeat_pos))
        if self.new_alarm_menu_lvl == 2:
            self.info_set("Playback source", sources[self.new_alarm.source][1])
        if self.new_alarm_menu_lvl == 3:
            self.info_set("Alarm set", "")

            #save alarm info here
            self.alarm_list.append(self.new_alarm)
            self.write_alarm_file()

            self.new_alarm = None
            self.new_repeat_pos = 0
            self.new_alarm_menu_lvl = 0

            time.sleep(1)
            self.show_alarm_info()

    # show alarm info
    # Cycle through alarms with button 3
    # Cycle through alarm fields with button 4
    # Modify alarm fields with keys 1/2
    def show_alarm_info(self):
        alarm = self.alarm_list[self.alarm_index]
        self.info_set("Alarm " + str(self.alarm_index),
                      "%02d:%02d %s" % (alarm.hours,
                                        alarm.minutes,
                                        self.get_repeat_string(alarm.repeat, None)))

    def show_cancel_alarm_confirmation(self):
        self.info_set(None, self.pointers[self.pointer_pos][0] + "No / Yes" +
                            self.pointers[self.pointer_pos][1])

    def button1(self):
        if self.alarm_cancel == True:
            self.pointer_pos = (self.pointer_pos + 1) % 2
            self.show_cancel_alarm_confirmation()
        elif self.new_alarm != None:
            if self.new_alarm_menu_lvl == 0:
                self.new_alarm.hours = (self.new_alarm.hours + 1) % 24
            elif self.new_alarm_menu_lvl == 1:
                self.new_repeat_pos = (self.new_repeat_pos + 1 ) % 7
            elif self.new_alarm_menu_lvl == 2:
                self.new_alarm.source -= 1
                if self.new_alarm.source < 0:
                    self.new_alarm.source = len(sources) - 1

            self.show_new_alarm_menu()

    def button2(self):
        if self.alarm_cancel == True:
            self.pointer_pos = (self.pointer_pos + 1) % 2
            self.show_cancel_alarm_confirmation()
        elif self.new_alarm != None:
            if self.new_alarm_menu_lvl == 0:
                self.new_alarm.minutes = (self.new_alarm.minutes + 5) % 60
            elif self.new_alarm_menu_lvl == 1:
                self.new_alarm.repeat = self.new_alarm.repeat ^ (1 << self.new_repeat_pos)
            elif self.new_alarm_menu_lvl == 2:
                self.new_alarm.source = (self.new_alarm.source + 1) % len(sources)

            self.show_new_alarm_menu()

    def start_new_alarm(self):
        self.new_alarm_menu_lvl = 0
        self.new_alarm = Alarm()
        self.new_repeat_pos = 0
        self.show_new_alarm_menu()

    # return -1 after last alarm in list, to return to clock mode
    def button3(self):
        if self.alarm_cancel == True:
            return 0
        elif self.new_alarm != None:
            # exit alarm_mode
            self.new_alarm = None
            self.alarm_index = -1
            return -1
        else:
            # cycling through alarms
            self.alarm_index += 1

            if self.alarm_index == len(self.alarm_list):
                # go into new alarm mode
                self.start_new_alarm()
            else:
                return self.show_alarm_info()

    # Show Cancel Alarm menu when in display info mode
    # Advance to next config menu in new alarm mode
    def button4(self):
        if self.new_alarm != None:
            self.new_alarm_menu_lvl += 1
            self.show_new_alarm_menu()
        else:
            if self.alarm_cancel == True:
                if self.pointer_pos == 1:
                    #confirmed
                    del self.alarm_list[self.alarm_index]
                    self.write_alarm_file()

                    self.info_set("Alarm Cleared", "")
                    time.sleep(1)
                    self.alarm_cancel = False
                    self.alarm_index -= 1

                    if self.alarm_index == -1:
                        self.alarm_index = 0
                        if len(self.alarm_list) > 0:
                            self.show_alarm_info()
                        else:
                            self.start_new_alarm()
                    else:
                        self.show_alarm_info()
                else:
                    #go back
                    self.alarm_cancel = False
                    self.show_alarm_info()
            else:
                self.info_set("Clear Alarm " + str(self.alarm_index) + "?", None)
                self.show_cancel_alarm_confirmation()
                self.alarm_cancel = True
