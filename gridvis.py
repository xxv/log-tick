#!/usr/bin/env python3

"""LevelUp transaction visualizer"""

import datetime
import json
import time
import sys

from apa102 import APA102
from mqtt_source import MQTTSource
from screen import ZigzagLedScreen

from patterns import ColorFadePattern

LED_SPEED = 16
LED_COUNT = 32
LED_GLOBAL_BRIGHTNESS = 31

def main():
    screen = ZigzagLedScreen(APA102(LED_COUNT, LED_GLOBAL_BRIGHTNESS), 5, 5, 1)
    pattern = ColorFadePattern(screen, LED_SPEED)
    source = MQTTSource(sys.argv[1])
    source.set_listener(pattern)
    source.connect()
    while True:
        pattern.tick()
        time.sleep(0.001)
        source.mqtt.loop()

if __name__ == "__main__":
    main()
