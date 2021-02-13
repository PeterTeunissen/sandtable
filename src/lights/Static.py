from ledable import Ledable

class Lighter(Ledable):
    def __init__(self, cols, rows):
        self.editor = []
        self.mode = 0

    def generator(self, leds, params):
        self.leds = leds
        self.params = params
        while True:
            yield True
