"""Basic module to load from LogEntries pull API"""

import time
import re
import urllib.request
import datetime
import iso8601

class LogEntries():
    def __init__(self, account_key, log_set_name, log_name):
        self.account_key = account_key
        self.log_set_name = log_set_name
        self.log_name = log_name

    def get_url(self, start, end, log_filter):
        return ("https://pull.logentries.com/"
                "{:s}/hosts/{:s}/{:s}/?start={:d}&end={:d}&filter={:s}".format(
                    self.account_key, self.log_set_name, self.log_name, start, end, log_filter))

    def load_logs(self, start, end, log_filter):
        try:
            response = urllib.request.urlopen(self.get_url(start, end, log_filter))
        except urllib.error.URLError as err:
            print("Error reading from network: %s" % err)
            return []
        body = response.read().decode('utf-8')
        events = []
        for line in body.split('\n'):
            match = re.match(r'.*?(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
                             r'.\d{6}[-+]\d{2}:\d{2}).*path="([^"]+)".*', line)
            if match:
                when = iso8601.parse_date(match.groups()[0])
                events.append((when, match.groups()[1]))

        return events

class LogEntriesWindow():
    def __init__(self, logentries, load_window, playback_offset):
        self.logentries = logentries
        self.load_window = load_window
        self.playback_offset = playback_offset
        self.last_load = None

    def to_microseconds(self, atime):
        return int(time.mktime(atime.timetuple()) * 1000 + atime.microsecond/1000)

    def load_events(self, log_filter, now=datetime.datetime.now()):
        events = []
        interval = int(self.load_window.total_seconds() * 1000)
        end = self.to_microseconds(now - self.playback_offset) + interval
        if self.last_load:
            delay = max(0, (self.last_load + interval/2) - end)
            if delay:
                return None, delay / 1000
        else:
            last_load = end - interval
        try:
            logs = self.logentries.load_logs(last_load, end, log_filter)
            for event in sorted(logs, key=lambda event: event[0]):
                events.append(event)
            print("Loaded {:d} events.".format(len(logs)))
            last_load = end

            return events, 0
        except urllib.error.HTTPError as err:
            if err.getcode() == 403: # ruh-ro! We may be polling too often.
                print("We've been throttled. Waiting a minute and trying again...")
                return None, 60
