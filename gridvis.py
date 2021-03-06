#!/usr/bin/env python3

"""LevelUp transaction visualizer"""

import sys

from apa102 import APA102
from anim import Animator
from mqtt_source import MQTTSource
from patterns import ColorFadePattern
from screen import ZigzagLedScreen

LED_SPEED = 16
LED_COUNT = 32
LED_GLOBAL_BRIGHTNESS = 31

def main():
    if len(sys.argv) != 2:
        print("Usage: {} MQTT_CONFIG".format(sys.argv[0]))
        sys.exit(1)

    screen = ZigzagLedScreen(APA102(LED_COUNT, LED_GLOBAL_BRIGHTNESS), 5, 5, 1)
    pattern = ColorFadePattern(screen, LED_SPEED)
    pattern.test()

    source = MQTTSource(sys.argv[1])
    source.connect()

    animator = Animator(source, pattern)
    animator.loop_forever()

if __name__ == "__main__":
    main()
