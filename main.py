import time
import random
import usb_midi
import adafruit_midi
import board
import digitalio
import math
from time import sleep
from adafruit_midi.control_change import ControlChange
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.pitch_bend import PitchBend
from analogio import AnalogIn

S0 = digitalio.DigitalInOut(board.GP2)
S1 = digitalio.DigitalInOut(board.GP3)
S2 = digitalio.DigitalInOut(board.GP4)
S3 = digitalio.DigitalInOut(board.GP5)

S4 = digitalio.DigitalInOut(board.GP10)
S5 = digitalio.DigitalInOut(board.GP11)
S6 = digitalio.DigitalInOut(board.GP12)
S7 = digitalio.DigitalInOut(board.GP13)

#Buttons INPUT
S0.direction = digitalio.Direction.OUTPUT
S1.direction = digitalio.Direction.OUTPUT
S2.direction = digitalio.Direction.OUTPUT
S3.direction = digitalio.Direction.OUTPUT
BUTT_SIG_PIN = AnalogIn(board.A0)

S4 = digitalio.DigitalInOut(board.GP6)
S5 = digitalio.DigitalInOut(board.GP7)
S6 = digitalio.DigitalInOut(board.GP8)
S7 = digitalio.DigitalInOut(board.GP9)

#Potentiometers INPUT
S4.direction = digitalio.Direction.OUTPUT
S5.direction = digitalio.Direction.OUTPUT
S6.direction = digitalio.Direction.OUTPUT
S7.direction = digitalio.Direction.OUTPUT
POT_SIG_PIN = AnalogOut(board.A1)

#LEDs OUTPUT
S8.direction = digitalio.Direction.OUTPUT
S9.direction = digitalio.Direction.OUTPUT
S10.direction = digitalio.Direction.OUTPUT
S11.direction = digitalio.Direction.OUTPUT
LED_SIG_PIN = AnalogOut(board.A2)

channelCount = 15

deadzone = 5
upperLimit = 120
lowerLimit = 11

defaultArray = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
defaultArray2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# Midi stuff
print(usb_midi.ports)
midi = adafruit_midi.MIDI(
    midi_in=usb_midi.ports[0], in_channel=0, midi_out=usb_midi.ports[1], out_channel=0
)
print("Midi test")
print("Default output channel:", midi.out_channel + 1)
print("Listening on input channel:", midi.in_channel + 1)


# functions
def debug_displayChart():
    print("hello")
    seperator = " | "
    topSeperator = "   |   "
    rows = ["  1   |   2   |   3   |   4   |   5   |   6   |   7   |  8  |  9  |  10  |  11  |  12  |  13  |  14", ""]
    channel = 1
    while channel <= channelCount:
        value = reading[channel - 1]
        displayValue = str(value)
        while len(str(displayValue)) < 5:
            displayValue += " "
        rows[1] += displayValue + seperator
        channel += 1
    for row in rows:
        print(row)


def read_multiplexed():
    channel = 0
    result = defaultArray2
    while channel < channelCount:  # Can go to 16 channels
        muxValue = readMux(channel)
        # Conversion
        value = math.floor((muxValue / 512))
        if value > upperLimit:
            value = 127
        if value < lowerLimit:
            value = 0
        result[channel] = value
        channel += 1
    return result


def readMux(channel):
    controlPins = [S0, S1, S2, S3]

    muxChannel = [
        [0, 0, 0, 0],#0
        [0, 0, 0, 1],#1
        [0, 0, 1, 0],#2
        [0, 0, 1, 1],#3
        [0, 1, 0, 0],#4
        [0, 1, 0, 1],#5
        [0, 1, 1, 0],#6

        [1, 1, 0, 0 ],#7
        [1, 0, 0, 0 ],#8
        [1, 0, 0, 1 ],#9
        [1, 0, 1, 0 ],#10
        [1, 0, 1, 1 ],#11
        [0, 1, 1, 1 ],#12
        [1, 1, 0, 1 ],#13
        [1, 1, 1, 1 ],#Unused
        [1, 1, 1, 0 ] #Unused
    ]

    i = 0
    while i < 4:
        controlPins[i].value = muxChannel[channel][i]
        i += 1
    value = SIG_PIN.value
    return value


def outputReading(note, value):
    print(note, value)
    #midi.send(NoteOn(note, value))
    #sleep(.001)
    midi.send(ControlChange(note, value))
    #sleep(.001)
    #midi.send(NoteOff(note, 0))

def readWriteButts(buttPins):
    i = length(buttPins)
    buttVals = []
    for butt in buttPins:
        buttVals[i] = butt.value
    return buttVals

def invertSliderValue(val):
    #This is surprisingly easy LUL
    val = 127 - val
    return val

# ---------------------------------------------------------------------------
readings = defaultArray
prevSettings = defaultArray
while True:
    #readWriteButts()
    lastReading = readings
    readings = read_multiplexed()
    i = 0
    for reading in readings:
        if prevSettings[i] - deadzone > reading or prevSettings[i] + deadzone < reading:
            if i > 6:
                outputReading(i, invertSliderValue(reading))
            else:
                outputReading(i, reading)
            prevSettings[i] = reading
        i += 1
