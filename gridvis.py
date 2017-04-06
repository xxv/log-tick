#!/usr/bin/env python3

"""LevelUp transaction visualizer"""

import datetime
import time
import threading
import random
import urllib.request
import queue
import json
import pytz
from apa102 import APA102
from logentries import LogEntries
from screen import ZigzagLedScreen

LED_COUNT = 32
LED_GLOBAL_BRIGHTNESS = 31
LED_SPEED = 16

MIN_BUFFER_SIZE = 10

ORANGE = 0xff7a00
BLUE = 0x2255ff
GREEN = 0x00ff00

# The window of time to load at once
LOAD_WINDOW = datetime.timedelta(seconds=60)

# negative offset from realtime
PLAYBACK_OFFSET = datetime.timedelta(seconds=65)

LOG_FILTER = '/router.*POST.*orders.*status=200/'

def fade_color(color, amount):
    color2 = (max(0, int((color >> 16) * amount))) << 16
    color2 |= (max(0, int((color >> 8 & 0xff) * amount))) << 8
    color2 |= max(0, int((color & 0xff) * amount))

    return color2

class LedPattern():
    screen = None
    points = []
    def __init__(self, screen, speed):
        self.screen = screen
        self.speed = speed
        self.counter = 0

    def clear(self):
        self.screen.clear()

    def tick(self):
        self.counter = (self.counter + 1) % self.speed
        if self.counter == 0:
            self.advance(0)

    def has_point(self, coord):
        if len(self.points) >= self.screen.width * self.screen.height:
            return True
        for point in self.points:
            if coord == point[0]:
                return True
        return False

    def add(self, value):
        if len(self.points) >= self.screen.width * self.screen.height:
            # filled. Just set it to be the position of the one that happened longest ago
            coord = self.points[0][0]
            del self.points[0]
            self.points.append([coord, value, 100])
        else:
            while True:
                x = random.randint(0, self.screen.width)
                y = random.randint(0, self.screen.height)
                coord = (x, y)
                if not self.has_point(coord):
                    break
            self.points.append([coord, value, 100])

    def advance(self, value):
        for point in self.points:
            point[2] -= 1
        self.points[:] = [l for l in self.points if l[2] > 0]
        self.show()

    def show(self):
        self.screen.clear()
        for point in self.points[:]:
            color = fade_color(point[1], (point[2])/100.0)
            self.screen.setPixel(point[0], color)
        self.screen.show()

    def test(self):
        self.screen.clear()
        self.screen.setPixel((4, 3), ORANGE)
        self.screen.setPixel((4, 4), BLUE)
        self.screen.setPixel((3, 4), GREEN)
        self.screen.show()

class Visualizer():
    events_queue = queue.Queue()
    load_lock = threading.Event()
    event = None

    def __init__(self, screen):
        try:
            self.leds = LedPattern(screen, LED_SPEED)
        except FileNotFoundError:
            self.leds = None

    def to_microseconds(self, atime):
        return int(time.mktime(atime.timetuple()) * 1000 + atime.microsecond/1000)

    def load_events(self):
        last_load = None
        config = None
        with open("/etc/order-sound.json") as config_file:
            config = json.load(config_file)
        logentries = LogEntries(config['account_key'], config['log_set_name'], config['log_name'])
        while True:
            self.load_lock.wait()
            print("Loading events...")

            interval = int(LOAD_WINDOW.total_seconds() * 1000)
            end = self.to_microseconds(datetime.datetime.now() - PLAYBACK_OFFSET) + interval
            if last_load:
                delay = max(0, (last_load + interval/2) - end)
                if delay:
                    print("Reloading too fast. Waiting...")
                time.sleep(delay / 1000)
                end = self.to_microseconds(datetime.datetime.now() - PLAYBACK_OFFSET) + interval
            else:
                last_load = end - interval
            try:
                logs = logentries.load_logs(last_load, end, LOG_FILTER)
                for event in sorted(logs, key=lambda event: event[0]):
                    self.events_queue.put(event)
                print("Loaded {:d} events.".format(len(logs)))
                last_load = end
                self.load_lock.clear()
            except urllib.error.HTTPError as err:
                if err.getcode() == 403: # ruh-ro! We may be polling too often.
                    print("We've been throttled. Waiting a minute and trying again...")
                    time.sleep(60)

    def display_event(self, event):
        print(event)
        color = ORANGE
        if 'v13' in event[1]:
            color = GREEN
        elif 'gift' in event[1] or 'v15' in event[1]:
            color = BLUE
        if self.leds:
            self.leds.add(color)

    def start(self):
        thread = threading.Thread(target=self.load_events)
        thread.daemon = True
        thread.start()

    def test_leds(self):
        if self.leds:
            self.leds.test()
            time.sleep(2)
            self.leds.clear()

    def tick(self):
        # if the buffer is low, fill it up
        if self.events_queue.qsize() < MIN_BUFFER_SIZE and not self.load_lock.is_set():
            self.load_lock.set()
        if not self.event:
            try:
                self.event = self.events_queue.get(block=False)
            except queue.Empty:
                self.event = None
        if self.event and (self.event[0] + PLAYBACK_OFFSET) <= datetime.datetime.now(tz=pytz.utc):
            self.display_event(self.event)
            self.event = None
        else:
            if self.leds:
                self.leds.tick()

def main():
    visualizer = Visualizer(ZigzagLedScreen(APA102(LED_COUNT, LED_GLOBAL_BRIGHTNESS), 5, 5, 1))
    visualizer.start()
    while True:
        visualizer.tick()
        time.sleep(0.001)

if __name__ == "__main__":
    main()
