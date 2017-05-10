#!/usr/bin/env python3

"""LevelUp transaction visualizer"""

import datetime
import json
import time
import sys

from apa102 import APA102
from mqtt_base import MQTTBase
from screen import ZigzagLedScreen

from patterns import ColorFadePattern

LED_SPEED = 16
LED_COUNT = 32
LED_GLOBAL_BRIGHTNESS = 31

class MQTTSource(MQTTBase):
    def __init__(self, config_file, pattern):
        MQTTBase.__init__(self, config_file=config_file)
        self.pattern = pattern

    def on_connect(self, client, userdata, flags, conn_result):
        self.mqtt.subscribe('levelup/visualization/order')
        print("Connected to MQTT.")

    def on_message(self, client, userdata, message):
        try:
            self.pattern.on_event(json.loads(message.payload.decode('utf-8')))
        except json.JSONDecodeError as err:
            print("Error decoding JSON: {}".format(err))

def main():
    screen = ZigzagLedScreen(APA102(LED_COUNT, LED_GLOBAL_BRIGHTNESS), 5, 5, 1)
    pattern = ColorFadePattern(screen, LED_SPEED)
    source = MQTTSource(sys.argv[1], pattern)
    while True:
        pattern.tick()
        time.sleep(0.001)
        source.mqtt.loop()

if __name__ == "__main__":
    main()
