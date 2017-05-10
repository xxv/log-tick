#!/usr/bin/env python3

"""LevelUp transaction visualizer"""

import datetime
import time
import sys

from apa102 import APA102
from mqtt_base import MQTTBase
from screen import ZigzagLedScreen
from vis import Visualizer, EventSource

from patterns import ColorFadePattern

LED_SPEED = 16
LED_COUNT = 32
LED_GLOBAL_BRIGHTNESS = 31

class MQTTSource(MQTTBase, EventSource):
    def __init__(self, config_file):
        MQTTBase.__init__(self, config_file=config_file)
    def events(self):
        pass

def main():
    screen = ZigzagLedScreen(APA102(LED_COUNT, LED_GLOBAL_BRIGHTNESS), 5, 5, 1)
    pattern = ColorFadePattern(screen, LED_SPEED)
    source = MQTTSource(sys.argv[1])
    visualizer = Visualizer(pattern, source)
    visualizer.start()
    while True:
        visualizer.tick()
        time.sleep(0.001)

if __name__ == "__main__":
    main()
