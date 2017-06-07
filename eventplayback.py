"""Event playback"""

import datetime
import time
import threading
import queue
import pytz

MIN_BUFFER_SIZE = 40

# The window of time to load at once
LOAD_WINDOW = datetime.timedelta(seconds=60)

# negative offset from realtime
PLAYBACK_OFFSET = datetime.timedelta(seconds=165)

class EventSource(object):
    def events(self, start, end):
        """Return a list of events"""
        pass
    def get_date(self, event):
        """Gets the date for the given event"""
        pass

class PlaybackTarget(object):
    def on_event(self, event):
        raise Exception("must implement this method")

class DebugTarget(PlaybackTarget):
    def on_event(self, event):
        print("Event: {}".format(event))

class EventPlayback(object):
    events_queue = queue.Queue()
    load_lock = threading.Event()
    event = None
    offset_event_time = None

    def __init__(self, target, event_source):
        self.target = target
        self.event_source = event_source

    def to_microseconds(self, atime):
        return int(time.mktime(atime.timetuple()) * 1000 + atime.microsecond/1000)

    def load_events(self):
        last_load = None
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
            events = self.event_source.events(last_load, end)
            for event in events:
                self.events_queue.put(event)
            print("Loaded {:d} events.".format(len(events)))
            last_load = end
            self.load_lock.clear()

    def start(self):
        thread = threading.Thread(target=self.load_events)
        thread.daemon = True
        thread.start()

    def tick(self):
        # if the buffer is low, fill it up
        if self.events_queue.qsize() < MIN_BUFFER_SIZE and not self.load_lock.is_set():
            self.load_lock.set()
        if not self.event:
            try:
                self.event = self.events_queue.get(block=False)
                self.offset_event_time = self.event_source.get_date(self.event) + PLAYBACK_OFFSET
            except queue.Empty:
                self.event = None
        if self.event and self.offset_event_time <= datetime.datetime.now(tz=pytz.utc):
            print('.', end='', flush=True)
            self.target.on_event(self.event)
            self.event = None
