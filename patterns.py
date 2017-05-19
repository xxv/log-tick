"""Visualization patterns"""

import random

ORANGE = 0xff7a00
BLUE = 0x2255ff
GREEN = 0x00ff00

def fade_color(color, amount):
    color2 = (max(0, int((color >> 16) * amount))) << 16
    color2 |= (max(0, int((color >> 8 & 0xff) * amount))) << 8
    color2 |= max(0, int((color & 0xff) * amount))

    return color2

class Pattern(object):
    """A visualization pattern"""
    def tick(self):
        """Call this on a regular basis to update any animation state"""
        pass
    def show_event(self, event):
        """Call this to add a new event to the visualization"""
        pass

class DebugPattern(Pattern):
    """A handy pattern that just prints out events"""
    def tick(self):
        pass
    def show_event(self, event):
        print("Event: {}".format(event))

class ColorFadePattern(Pattern):
    """Displays fading colors on a screen"""
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
            self.advance()

    def has_point(self, coord):
        if len(self.points) >= self.screen.width * self.screen.height:
            return True
        for point in self.points:
            if coord == point[0]:
                return True
        return False

    def show_event(self, event):
        color = ORANGE
        if 'v13' in event['path']:
            color = GREEN
        elif 'order_ahead' in event['path'] or 'gift' in event['path'] or 'v15' in event['path']:
            color = BLUE

        self.add_color(color)

    def add_color(self, value):
        """Add the given color to the display"""
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

    def advance(self):
        for point in self.points:
            point[2] -= 1
        self.points[:] = [l for l in self.points if l[2] > 0]
        self.show()

    def show(self):
        self.screen.clear()
        for point in self.points[:]:
            color = fade_color(point[1], (point[2])/100.0)
            self.screen.set_pixel(point[0], color)
        self.screen.show()

    def test(self):
        self.screen.clear()
        self.screen.set_pixel((4, 3), ORANGE)
        self.screen.set_pixel((4, 4), BLUE)
        self.screen.set_pixel((3, 4), GREEN)
        self.screen.show()
