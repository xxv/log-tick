import json
from eventplayback import EventSource
from mqtt_base import MQTTBase

class MQTTSource(MQTTBase, EventSource):
    listener = None
    topic = 'levelup/visualization/order'

    def __init__(self, config_file):
        MQTTBase.__init__(self, config_file=config_file)

    def events(self):
        return []

    def set_listener(self, listener):
        self.listener = listener

    def on_connect(self, client, userdata, flags, conn_result):
        self.mqtt.subscribe(self.topic)
        print("Connected to MQTT server.")

    def on_message(self, client, userdata, message):
        if self.topic == message.topic:
            try:
                self.on_order(json.loads(message.payload.decode('utf-8')))
            except ValueError as err:
                print("Ignoring message that could not be decoded: {}".format(message.payload.decode('utf-8')))

    def on_order(self, body):
        if self.listener:
            self.listener(body)
