#!/usr/bin/env python3

"""LevelUp transaction visualizer"""

import datetime
import queue
import json
import time
import sys

from apa102 import APA102
from mqtt_source import MQTTSource
from screen import ZigzagLedScreen
from threading import Thread

from patterns import ColorFadePattern

LED_SPEED = 16
LED_COUNT = 32
LED_GLOBAL_BRIGHTNESS = 31

class Animator(object):
    event_queue = queue.Queue()

    def __init__(self, source, pattern):
        self.source = source
        self.pattern = pattern
        source.set_listener(self.enqueue_event)

    def enqueue_event(self, event):
        self.event_queue.put(event)

    def process_queue(self):
        try:
            while True:
                self.pattern.show_event(self.event_queue.get(block=False))
        except queue.Empty:
            pass

    def loop_forever(self):
        Thread(target=self.source.loop_forever).start()
        print("Looping forever")
        while True:
            self.process_queue()
            self.pattern.tick()
            time.sleep(0.001)

def main():
    screen = ZigzagLedScreen(APA102(LED_COUNT, LED_GLOBAL_BRIGHTNESS), 5, 5, 1)
    pattern = ColorFadePattern(screen, LED_SPEED)
    pattern.test()
    source = MQTTSource(sys.argv[1])
    source.connect()
    animator = Animator(source, pattern)
    animator.loop_forever()

if __name__ == "__main__":
    main()
