#!/usr/bin/env python3

"""Sample LevelUp transaction visualizer"""

import sys

from anim import Animator
from mqtt_source import MQTTSource
from patterns import DebugPattern

def main():
    if len(sys.argv) != 2:
        print("Usage: {} MQTT_CONFIG".format(sys.argv[0]))
        sys.exit(1)

    pattern = DebugPattern()
    source = MQTTSource(sys.argv[1])
    source.connect()

    animator = Animator(source, pattern)
    animator.loop_forever()

if __name__ == "__main__":
    main()
