"""Logentries -> MQTT"""

import json
import time
import sys
from threading import Thread

from mqtt_base import MQTTBase
from eventplayback import EventPlayback, PlaybackTarget
from dataclip_source import DataClipSource

class MQTTTarget(MQTTBase, PlaybackTarget):
    topic = 'levelup/visualization/order'

    def __init__(self, config_file):
        MQTTBase.__init__(self, config_file=config_file)

    def on_connect(self, client, userdata, flags, conn_result):
        print("Connected to MQTT server.")

    def on_event(self, event):
        self.mqtt.publish(self.topic, json.dumps(event))

def main():
    target = MQTTTarget(sys.argv[1])
    target.connect()
    mqtt_thread = Thread(target=target.loop_forever)
    mqtt_thread.start()
    source = DataClipSource(sys.argv[2])
    event_playback = EventPlayback(target, source)
    event_playback.start()
    while True:
        event_playback.tick()
        time.sleep(0.001)

if __name__ == "__main__":
    main()
