"""Components for animating visualizations"""

import queue
import time

from threading import Thread
class Animator(object):
    """Animates events from the source using the pattern

    This queues events and runs the source loop on a background
    thread so the animation is smooth."""

    event_queue = queue.Queue()

    def __init__(self, source, pattern):
        self.source = source
        self.pattern = pattern
        source.set_listener(self.enqueue_event)

    def enqueue_event(self, event):
        self.event_queue.put(event)

    def process_queue(self):
        try:
            while True:
                self.pattern.show_event(self.event_queue.get(block=False))
        except queue.Empty:
            pass

    def loop_forever(self):
        Thread(target=self.source.loop_forever).start()
        print("Animation started.")
        while True:
            self.process_queue()
            self.pattern.tick()
            time.sleep(0.001)
