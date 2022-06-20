#!/usr/bin/env python

import unittest
import pr_alarm_manager as alarm_mod

class TestAlarmModule(unittest.TestCase):
    alarm_mgr = None
    line1 = ""
    line2 = ""

    def alarm_cb(self):
        pass

    def info_set(self, value1, value2):
        if value1 != None:
            self.line1 = value1
        if value2 != None:
            self.line2 = value2

    def step_helper(self, steps):
        # when multiple button presses are defined in a step
        # buttons are pressed in sequence 1->2->3->4

        print(" " + self._testMethodName)

        buttons = [ self.alarm_mgr.button1,
                    self.alarm_mgr.button2,
                    self.alarm_mgr.button3,
                    self.alarm_mgr.button4]

        for step in range(0, len(steps)):
            print(str(step), end = " ")
            for i in range(0, 4):
                for j in range(0, steps[step][i]):
                    buttons[i]()

            if steps[step][4] != None:
                assert self.line1 == steps[step][4], "step %d, expecting line1 \"%s\", got \"%s\"" % (step, steps[step][4], self.line1)
            if steps[step][5] != None:
                assert self.line2 == steps[step][5], "step %d, expecting line2 \"%s\", got \"%s\"" % (step, steps[step][5], self.line2)
        print("")

    def setUp(self):
        self.alarm_mgr = alarm_mod.alarm_manager(self.info_set, self.alarm_cb)
        self.alarm_mgr.alarm_list = []
        self.alarm_mgr.alarms_file = "test_alarms.txt"

        alarm_mod.sources = [["url", "netradio", "stream"],
                             ["m3u", "local", "list"]]

    def tearDown(self):
        pass

    def testAddNewAlarmEmptyList(self):
        steps = [ #b1, b2, b3, b4, line1, line2
                  [ 0,  0,  1,  0, "New Alarm", "00:00"],
                  [ 8,  6,  0,  0, "New Alarm", "08:30"],
                  [ 0,  0,  0,  1, "Repeat?", "*m t w t f s s"],
                  [ 0,  1,  0,  0, "Repeat?", "*M t w t f s s"],
                  [ 1,  1,  0,  0, "Repeat?", " M*T w t f s s"],
                  [ 3,  1,  0,  0, "Repeat?", " M T w t*F s s"],
                  [ 0,  0,  0,  1, "Playback source", alarm_mod.sources[0][1]],
                  [ 0,  1,  0,  0, "Playback source", alarm_mod.sources[1][1]],
                  [ 0,  1,  0,  0, "Playback source", alarm_mod.sources[0][1]],
                  [ 1,  0,  0,  0, "Playback source", alarm_mod.sources[1][1]],
                  [ 0,  0,  0,  1, "Alarm 0", "08:30 MTwtFss"],
                ]

        self.step_helper(steps)

    def testAddNewAlarmNonEmptyList(self):
        steps = [ #b1, b2, b3, b4, line1, line2
                  [ 0,  0,  1,  0, "Alarm 0", "06:00 MTWTFss"],
                  [ 0,  0,  1,  0, "New Alarm", "00:00"],
                  [ 8,  6,  0,  0, "New Alarm", "08:30"],
                  [ 0,  0,  0,  1, "Repeat?", "*m t w t f s s"],
                  [ 0,  0,  0,  1, "Playback source", alarm_mod.sources[0][1]],
                  [ 0,  1,  0,  0, "Playback source", alarm_mod.sources[1][1]],
                  [ 0,  0,  0,  1, "Alarm 1", "08:30 mtwtfss"],
                ]

        self.alarm_mgr.alarm_list.append(alarm_mod.Alarm([6, 0, 31, 1]))
        self.step_helper(steps)

    def testDeleteFinalAlarmAndAddNew(self):
        steps = [ #b1, b2, b3, b4, line1, line2
                  [ 0,  0,  1,  0, "Alarm 0", "06:00 MTWTFss"],
                  [ 0,  0,  0,  1, "Clear Alarm 0?", " * No / Yes   "],
                    # cancel delete
                  [ 0,  0,  0,  1, "Alarm 0", "06:00 MTWTFss"],
                    # start again
                  [ 0,  0,  0,  1, "Clear Alarm 0?", " * No / Yes   "],
                  [ 1,  0,  0,  0, "Clear Alarm 0?", "   No / Yes * "],
                  [ 0,  1,  0,  0, "Clear Alarm 0?", " * No / Yes   "],
                  [ 0,  1,  0,  0, "Clear Alarm 0?", "   No / Yes * "],
                    # confirm delete
                  [ 0,  0,  0,  1, "New Alarm", "00:00"],
                  [ 0,  0,  0,  1, "Repeat?", "*m t w t f s s"],
                  [ 0,  0,  0,  1, "Playback source", alarm_mod.sources[0][1]],
                  [ 0,  0,  0,  1, "Alarm 0", "00:00 mtwtfss"],
                ]

        self.alarm_mgr.alarm_list.append(alarm_mod.Alarm([6, 0, 31, 1]))
        self.step_helper(steps)

    def testDeleteNonFinalAlarm(self):
        steps = [ #b1, b2, b3, b4, line1, line2
                  [ 0,  0,  1,  0, "Alarm 0", "06:00 MTWTFss"],
                  [ 0,  0,  0,  1, "Clear Alarm 0?", " * No / Yes   "],
                  [ 1,  0,  0,  0, "Clear Alarm 0?", "   No / Yes * "],
                    # confirm delete
                  [ 0,  0,  0,  1, "Alarm 0", "09:30 mtwtfss"],
                ]

        self.alarm_mgr.alarm_list.append(alarm_mod.Alarm([6,  0, 31, 1]))
        self.alarm_mgr.alarm_list.append(alarm_mod.Alarm([9, 30,  0, 1]))
        self.step_helper(steps)

if __name__ == '__main__':
    unittest.main()
