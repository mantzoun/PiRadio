class alarm_manager:
    alarm_list = []
    alarm_index = 0
    info_set = None
    alarm_cb = None

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

    def parse_alarm(self, alarm_line):
        alarm_info = alarm_line.split(",")
        if len(alarm_info) != 4:
            print("error alarm " + alarm_info)
            return -1
        return alarm_info

    # show alarm info
    # Cycle through alarms with button 3
    # Cycle through alarm fields with button 4
    # Modify alarm fields with keys 1/2
    # return -1 after last alarm in list, to return to clock mode
    def show_alarm_info(self):
        if len(self.alarm_list) > 0:
            return self.alarm_list[self.alarm_index]
