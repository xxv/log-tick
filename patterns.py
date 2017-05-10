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
    def clear(self):
        pass
    def tick(self):
        pass
    def show_event(self, event):
        pass
    def test(self):
        pass

class DebugPattern(Pattern):
    def clear(self):
        print("Clear")
    def tick(self):
        pass
    def show_event(self, event):
        print("Event: {}".format(event))
    def test(self):
        print("Test")

class ColorFadePattern(object):
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
            self.advance(0)

    def has_point(self, coord):
        if len(self.points) >= self.screen.width * self.screen.height:
            return True
        for point in self.points:
            if coord == point[0]:
                return True
        return False

    def show_event(self, event):
        print("{} {}".format(event[0].isoformat(), event[1]))
        color = ORANGE
        if 'v13' in event[1]:
            color = GREEN
        elif 'gift' in event[1] or 'v15' in event[1]:
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

    def advance(self, value):
        for point in self.points:
            point[2] -= 1
        self.points[:] = [l for l in self.points if l[2] > 0]
        self.show()

    def show(self):
        self.screen.clear()
        for point in self.points[:]:
            color = fade_color(point[1], (point[2])/100.0)
            self.screen.setPixel(point[0], color)
        self.screen.show()

    def test(self):
        self.screen.clear()
        self.screen.setPixel((4, 3), ORANGE)
        self.screen.setPixel((4, 4), BLUE)
        self.screen.setPixel((3, 4), GREEN)
        self.screen.show()
