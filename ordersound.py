#!/usr/bin/env python3

import datetime
import json
import re
import sounddevice as sd
import time
import urllib.request

def get_url(account_key, log_set_name, log_name, start, end):
    return "https://pull.logentries.com/{:s}/hosts/{:s}/{:s}/?start={:d}&end={:d}&filter=/router.*POST.*orders\"/".format(account_key, log_set_name, log_name, start, end)

def load_logs(account_key, log_set_name, log_name):
    interval=60
    when=int(time.time() * 1000)

    r=urllib.request.urlopen(get_url(account_key, log_set_name, log_name, when-(interval * 1000), when))
    body=r.read().decode('utf-8')
    events=[]
    for line in body.split('\n'):
        m = re.match(r'.*?(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{6}[-+]\d{2}:\d{2}).*path="([^"]+)".*', line)
        if m:
            when=datetime.datetime.strptime(m.groups()[0], '%Y-%m-%dT%H:%M:%S.%f+00:00')
            events.append((when, m.groups()[1]))

    return events


def play_events(events):
    fs=44100

    prev = None
    for event in sorted(events, key=lambda event: event[0]):
        if prev:
            delay=event[0] - prev
        else:
            delay=datetime.timedelta(0)
        prev = event[0]
        time.sleep(delay.total_seconds())
        sd.play([[-1.0],[-1.0],[-1.0], [0.0]], fs, blocking=True)

config = None
with open("config.json") as config_file:
    config=json.load(config_file)

play_events(load_logs(config['account_key'], config['log_set_name'], config['log_name']))
