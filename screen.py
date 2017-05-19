"""A simple 2D screen"""

class Screen:
    """A simple 2D display"""
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def set_pixel(self, pixel, value):
        """Set the pixel to the given value"""
        pass

    def show(self):
        """Refresh the display"""
        pass

    def clear(self):
        """Clear the display"""
        pass

class ZigzagLedScreen(Screen):
    """A screen that maps a is made using a zig-zag LED strip"""
    def __init__(self, leds, width, height, initial_offset=0):
        Screen.__init__(self, width, height)
        self.leds = leds
        self.initial_offset = initial_offset

    def map_pixel(self, pixel):
        """maps a pixel to a linear offset in the LED array"""
        # even rows
        if pixel[1] % 2 == 0:
            return pixel[1] * self.width + pixel[0] + self.initial_offset
        else:
            return pixel[1] * self.width + (self.width - pixel[0] - 1) + self.initial_offset

    def set_pixel(self, pixel, value):
        self.leds.setPixelRGB(self.map_pixel(pixel), value)

    def show(self):
        self.leds.show()

    def clear(self):
        for pos in range(0, self.width * self.height + self.initial_offset):
            self.leds.setPixelRGB(pos, 0)
