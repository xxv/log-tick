"""Logentries event source"""
import json
import time
import urllib
import urllib.request

from eventplayback import EventSource
from logentries import LogEntries

class LogEntriesSource(EventSource):
    def __init__(self, config_file):
        config = None
        with open(config_file) as config_in:
            config = json.load(config_in)
            self.log_filter = config['log_filter']
            self.logentries = LogEntries(config['account_key'], config['log_set_name'], config['log_name'])

    def events(self, start, end):
        try:
            logs = self.logentries.load_logs(start, end, self.log_filter)
            return sorted(logs, key=lambda event: event[0])
        except urllib.error.HTTPError as err:
            if err.getcode() == 403: # ruh-ro! We may be polling too often.
                print("We've been throttled. Waiting a minute and trying again...")
                time.sleep(60)
        return []
