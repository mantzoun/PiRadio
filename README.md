# PiRadio

## What is it?

This is a script that is meant to be executed on a Raspberry Pi and does three things:
   * acts as a wrapper for `mplayer`, and therefore is able to control media playback
   * controls a 16x2 LCD display connected to the Pi via i2c
   * Receives GPIO inputs

## What does it do?

Currently, the script can be in one of two modes, clock or media player. Depending 
on which one it is in, relevant information will be displayed on the LCD

### Clock mode

When in clock mode, the date and time are displayed, and an alarm clock function 
is planned for implementation.

### Media player mode

When in media player mode, the script will run an `mplayer` instance, with one 
of the streams or playlists defined in the `streams` array. The LCD will display 
information about the source selected, and the currently playing song.

## I2C LCD library
The i2c lcd library was written by Denis Pleic. More information can be found 
at the top of the library file.

## Controls
Four switches are connected to GPIOs. Two control playback volume and track selection, 
one is a play/stop button, and the last is a source selector.

## More information
The whole thing was packaged in a PJ Masks lunchbox and gifted to my kids. More 
information on the project can be found [here](https://www.mantzouneas.gr/projects/piradio/) (page in Greek).
