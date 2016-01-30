#!/usr/bin/env python3

import collections
import datetime
import json
import re
import sounddevice as sd
import time
import threading
import urllib.request
import queue
from apa102 import APA102

class LogEntries():
    def __init__(self, account_key, log_set_name, log_name):
        self.account_key = account_key
        self.log_set_name = log_set_name
        self.log_name = log_name

    def get_url(self, start, end):
        log_filter='/router.*POST.*orders\".*status=200/'
        return "https://pull.logentries.com/{:s}/hosts/{:s}/{:s}/?start={:d}&end={:d}&filter={:s}".format(self.account_key, self.log_set_name, self.log_name, start, end, log_filter)

    def load_logs(self, start, end):
        r=urllib.request.urlopen(self.get_url(start, end))
        body=r.read().decode('utf-8')
        events=[]
        for line in body.split('\n'):
            m = re.match(r'.*?(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{6}[-+]\d{2}:\d{2}).*path="([^"]+)".*', line)
            if m:
                when=datetime.datetime.strptime(m.groups()[0], '%Y-%m-%dT%H:%M:%S.%f+00:00')
                events.append((when, m.groups()[1]))

        return events

class LedPattern():
    buff=None
    def __init__(self, leds, count, speed):
        self.leds = leds
        self.buff = collections.deque([0] * count, count)
        self.speed = speed
        self.counter = 0

    def tick(self):
        self.counter = (self.counter + 1) % self.speed
        if self.counter == 0:
            self.advance(0)

    def advance(self, value):
        self.buff.appendleft(value)
        self.show()

    def show(self):
        for i, rgb in enumerate(self.buff):
            self.leds.setPixelRGB(i, rgb)
        self.leds.show()

events = queue.Queue()
load_lock = threading.Event()

def load_events():
    last_load=None
    config = None
    with open("config.json") as config_file:
        config=json.load(config_file)
    logentries = LogEntries(config['account_key'], config['log_set_name'], config['log_name'])
    while True:
        load_lock.wait()
        print("Loading events...")

        interval=60 * 1000
        now=int(time.time() * 1000)
        if last_load:
            delay = max(0, (last_load + interval/2) - now)
            if delay:
                print("Reloading too fast. Waiting...")
            time.sleep(delay / 1000)
            now=int(time.time() * 1000)
        else:
            last_load = now - interval
        logs = logentries.load_logs(last_load, now)
        for event in sorted(logs, key=lambda event: event[0]):
            events.put(event)
        print("Loaded {:d} events.".format(len(logs)))
        last_load = now
        load_lock.clear()

t = threading.Thread(target=load_events)
t.daemon=True
t.start()

# offset from realtime
offset=datetime.timedelta(seconds=60 + 5)

led_count=32
fs=44100
leds=LedPattern(APA102(led_count), led_count, 32)

#RRBBGG
#          RRBBGG
ORANGE = 0xff007a
BLUE   = 0x75b0ff
GREEN  = 0x0000ff

event = None
while True:
    # if the buffer is low, fill it up
    if events.qsize() < 5 and not load_lock.is_set():
        load_lock.set()
    if not event:
        try:
            event = events.get(block=False)
        except queue.Empty:
            event = None
    if event and (event[0] + offset) <= datetime.datetime.now():
        sd.play([[-1.0],[-1.0],[-1.0], [0.0]], fs, blocking=False)
        print(event)
        try:
            event = events.get(block=False)
            color=ORANGE
            if 'v13' in event[1]:
                color=GREEN
            elif 'gift' in event[1]:
                color=BLUE
            leds.advance(color)
        except queue.Empty:
            event = None
    else:
        leds.tick()
    time.sleep(0.001)
