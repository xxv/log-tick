"""Heroku dataclip event source"""
import csv
import json
import time
import urllib
import urllib.request
import requests
import dateutil.parser
from datetime import datetime

from eventplayback import EventSource

class DataClipSource(EventSource):
    date_parser = dateutil.parser
    def __init__(self, config_file):
        config = None
        with open(config_file) as config_in:
            config = json.load(config_in)
            self.url = config['url']

    def get_date(self, event):
        return self.date_parser.parse(event['created_at']+'Z')

    def read_clip(self):
        result = requests.get(self.url)

        if result.status_code == 200:
            return list(csv.DictReader(result.text.splitlines()))
        else:
            print("Error accessing data: {}".format(result))
            return []

    def events(self, start, end):
        print("Window: {} and {}".format(datetime.fromtimestamp(start/1000), datetime.fromtimestamp(end/1000)))
        try:
            unfiltered_events = self.read_clip()
            events = [event for event in unfiltered_events if start <= (self.get_date(event).timestamp() * 1000) < end]
            events_earlier = [event for event in unfiltered_events if (self.get_date(event).timestamp() * 1000) < start]
            events_later = [event for event in unfiltered_events if (self.get_date(event).timestamp() * 1000) >= end]
            print("{:d}/{:d} events in window ({:d} earlier, {:d} later)".format(len(events), len(unfiltered_events), len(events_earlier), len(events_later)))
            if unfiltered_events:
                print("First is {} last is {}".format(self.get_date(unfiltered_events[0]), self.get_date(unfiltered_events[-1])))

            return events

        except urllib.error.HTTPError as err:
            if err.getcode() == 403: # ruh-ro! We may be polling too often.
                print("We've been throttled. Waiting a minute and trying again...")
                time.sleep(60)
        return []
