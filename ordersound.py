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

def get_url(account_key, log_set_name, log_name, start, end):
    return "https://pull.logentries.com/{:s}/hosts/{:s}/{:s}/?start={:d}&end={:d}&filter=/router.*POST.*orders\"/".format(account_key, log_set_name, log_name, start, end)

def load_logs(account_key, log_set_name, log_name, start, end):
    r=urllib.request.urlopen(get_url(account_key, log_set_name, log_name, start, end))
    body=r.read().decode('utf-8')
    events=[]
    for line in body.split('\n'):
        m = re.match(r'.*?(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{6}[-+]\d{2}:\d{2}).*path="([^"]+)".*', line)
        if m:
            when=datetime.datetime.strptime(m.groups()[0], '%Y-%m-%dT%H:%M:%S.%f+00:00')
            events.append((when, m.groups()[1]))

    return events

class LedPattern():
    buffer=None
    def __init__(self, leds, count, speed):
        self.leds = leds
        self.buffer = collections.deque([0] * count, count)
        self.speed = speed
        self.counter = 0

    def tick(self):
        self.counter = (self.counter + 1) % self.speed
        if self.counter == 0:
            self.advance(0)

    def advance(self, value):
        self.buffer.appendleft(value)
        self.show()

    def show(self):
        for i, rgb in enumerate(self.buffer):
            self.leds.setPixelRGB(i, rgb)
        self.leds.show()

config = None
with open("config.json") as config_file:
    config=json.load(config_file)

events = queue.Queue()
load_lock = threading.Event()

def load_events():
    last_load=None
    while True:
        load_lock.wait() 
        print("Loading events...")

        interval=60 * 1000
        now=int(time.time() * 1000)
        if last_load:
            delay = max(0, (last_load + interval) - now)
            if delay:
                print("Reloading too fast. Waiting...")
            time.sleep(delay / 1000)
            now=int(time.time() * 1000)
        else:
            last_load = now - interval
        logs = load_logs(config['account_key'], config['log_set_name'], config['log_name'], last_load, now)
        for event in sorted(logs, key=lambda event: event[0]):
            events.put(event)
        print("Loaded {:d} events.".format(len(logs)))
        last_load = now
        load_lock.clear()

t = threading.Thread(target=load_events)
t.daemon=True
t.start()

# offset from realtime
offset=datetime.timedelta(seconds=65)

leds=LedPattern(APA102(32), 32, 32)
fs=44100

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
        except queue.Empty:
            event = None
        leds.advance(0xff007a)
    else:
        leds.tick()
    time.sleep(0.001)
