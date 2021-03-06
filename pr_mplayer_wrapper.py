#!/usr/bin/python

import subprocess
import os
import re
import signal

from threading import Thread

class mplayer_wrapper:
    player_proc = None
    debug = False
    out_t = None

    # Set the interface to the LCD controller, so as to pass
    # media information
    def __init__(self, info_set):
        self.info_set = info_set

    # Boolean that indicates if the player is running
    def on(self):
        if self.player_proc == None:
            return False
        return True

    # Parse the player output for relevant information. Of course needs
    # to be highly specific. Current implemantion, which uses mplayer
    # for playback, can capture ICY StreamTitle tag for currently playing
    # song in radio stream, or can parse song filename based on path
    def parse_output(self):
        while self.player_proc != None:
            line = self.player_proc.stdout.readline().decode('utf-8')

            if 'Volume' in line:
                splt = re.split(r'Volume: |\n', line)
                print(splt[1])
                self.info_set("volume", splt[1])
            elif 'StreamTitle' in line:
                splt = re.split(r'Title=\'|\';\n', line)
                print(splt[1])
                self.info_set("title", (self.to_ascii(splt[1])))
            elif 'Playing /home/pi' in line:
                splt = re.split(r'Playing /home/pi/music/|.mp3', line)
                print(splt[1])
                self.info_set("title", (self.to_ascii(splt[1])))

    # Start the output parser
    def start_output_thread(self):
        self.out_t = Thread(target = self.parse_output, args = ())
        self.out_t.start()

    # My LCD will not display greek characters, so do a rough transformation to latin"
    def to_ascii(self, str_in):
        char_map = str_in.maketrans("ΆΑάαΒβΓγΔδΈΕέεΖζΉΗήηΘθΊΙίιΚκΛλΜμΝνΞξΌΟόοΠπΡρΣσςΤτΎΥύυΦφΧχΨψΏΩώω",
                                    "AAaaBbGgDdEEeeZzHHhh88IIiiKkLlMmNn33OOooPpRrSssTtYYuuFfXxCcWWww");

        str_out = str_in.translate(char_map)
        return str_out

    # Start mplayer in a different thread, and use the in/out pipes for
    # playback control and information
    def start(self, stream_url, title, type):

        if self.debug == True:
            err_out=subprocess.PIPE
        else:
            err_out=subprocess.DEVNULL

        if type == "stream":
            cmd = ['/usr/bin/mplayer', '-channels', '1', '-quiet', stream_url]
        elif type == "list":
            cmd = ['/usr/bin/mplayer', '-channels', '1', '-quiet', '-loop', '0', '-playlist', stream_url]

        self.player_proc = subprocess.Popen(cmd,
                                        shell=False,
                                        preexec_fn=os.setsid,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=err_out)

        self.info_set("stream_title", title)
        self.start_output_thread()

    # Kill the mplayer process
    # TODO: should probably add some mplayer shortcut to exit gracefully
    def stop(self):
        os.killpg(os.getpgid(self.player_proc.pid), signal.SIGTERM)
        self.player_proc = None
        self.info_set("stream_title", "")
        self.info_set("title", "")

    def prev_track(self):
        self.player_proc.stdin.write(b'<')
        self.player_proc.stdin.flush()

    def next_track(self):
        self.player_proc.stdin.write(b'>')
        self.player_proc.stdin.flush()

    def vol_down(self):
        self.player_proc.stdin.write(b'/')
        self.player_proc.stdin.flush()

    def vol_up(self):
        self.player_proc.stdin.write(b'*')
        self.player_proc.stdin.flush()
