class ZigzagLedScreen:
    def __init__(self, leds, width, height, initial_offset=0):
        self.leds = leds
        self.width = width
        self.height = height
        self.initial_offset = initial_offset

    def map_pixel(self, pixel):
        # even rows
        if pixel[1] % 2 == 0:
            return pixel[1] * self.width + pixel[0] + self.initial_offset
        else:
            return pixel[1] * self.width + (self.width - pixel[0] - 1) + self.initial_offset

    def setPixel(self, pixel, value):
        self.leds.setPixelRGB(self.map_pixel(pixel), value)

    def show(self):
        self.leds.show()

    def clear(self):
        for n in range(0, self.width * self.height + self.initial_offset):
            self.leds.setPixelRGB(n, 0)
