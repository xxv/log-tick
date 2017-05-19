#!/usr/bin/env python3

"""Sample LevelUp transaction visualizer"""

import sys

from anim import Animator
from mqtt_source import MQTTSource
from patterns import Pattern

class SamplePattern(Pattern):
    """A simple demo pattern"""
    def tick(self):
        """This gets called on a regular basis."""
        # You can update any animation state here.
        pass
    def show_event(self, event):
        """This gets called when a new event comes in"""
        print("Event: {}".format(event))

def main():
    if len(sys.argv) != 2:
        print("Usage: {} MQTT_CONFIG".format(sys.argv[0]))
        sys.exit(1)

    pattern = SamplePattern()
    source = MQTTSource(sys.argv[1])
    source.connect()

    animator = Animator(source, pattern)
    animator.loop_forever()

if __name__ == "__main__":
    main()
