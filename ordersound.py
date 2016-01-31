#!/usr/bin/env python3

import collections
import datetime
import json
import iso8601
import pytz
import re
import rtmidi
from rtmidi.midiconstants import *
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
                when=iso8601.parse_date(m.groups()[0])
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

# offset from realtime
#load_offset     = datetime.timedelta(seconds = 5)
load_window     = datetime.timedelta(seconds = 60)
playback_offset = datetime.timedelta(days=4,hours=9,seconds = 65)

def to_microseconds(atime):
    return int(time.mktime(atime.timetuple()) * 1000 + atime.microsecond/1000)

def load_events():
    last_load=None
    config = None
    with open("config.json") as config_file:
        config=json.load(config_file)
    logentries = LogEntries(config['account_key'], config['log_set_name'], config['log_name'])
    while True:
        load_lock.wait()
        print("Loading events...")

        interval=int(load_window.total_seconds() * 1000)
        end=to_microseconds(datetime.datetime.now() - playback_offset) + interval
        if last_load:
            delay = max(0, (last_load + interval/2) - end)
            if delay:
                print("Reloading too fast. Waiting...")
            time.sleep(delay / 1000)
            end=to_microseconds(datetime.datetime.now() - playback_offset) + interval
        else:
            last_load = end - interval
        print(last_load, end)
        logs = logentries.load_logs(last_load, end)
        for event in sorted(logs, key=lambda event: event[0]):
            events.put(event)
        print("Loaded {:d} events.".format(len(logs)))
        last_load = end
        load_lock.clear()

t = threading.Thread(target=load_events)
t.daemon=True
t.start()

led_count=32
fs=44100
try:
    leds = LedPattern(APA102(led_count), led_count, 32)
except FileNotFoundError:
    leds = None

midiout = rtmidi.MidiOut()
midiout.open_port(5)

#RRBBGG
#          RRBBGG
ORANGE = 0xff007a
BLUE   = 0x75b0ff
GREEN  = 0x0000ff

def display_event(event):
    print(event)
    note = 60
    color = ORANGE
    if 'v13' in event[1]:
        color = GREEN
        note = 62
    elif 'gift' in event[1]:
        color = BLUE
        note = 64
    if leds:
        leds.advance(color)
    midiout.send_message((NOTE_ON | 10, note, 127))

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
    if event and (event[0] + playback_offset) <= datetime.datetime.now(tz=pytz.utc):
        display_event(event)
        event = None
    else:
        if leds:
            leds.tick()
    time.sleep(0.001)

del midiout
