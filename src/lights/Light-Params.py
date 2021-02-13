from dialog import DialogInt
from dialog import DialogColor 
from dialog import DialogTrueFalse
from ledable import Ledable


class Lighter(Ledable):
    def __init__(self, cols, rows):
        self.mode = -1
        self.editor = [
            DialogColor("color", "Color", default=(255, 0, 0)),
            DialogInt("speed", "Speed", default=1000, min=1, max=65535),
            DialogInt("brightness", "Brightness", default=50, min=1, max=255),
	        DialogTrueFalse("autoCycle", "Auto Cycle", default=False)
        ]

    def generator(self, leds, params):
        leds.setColor(params.color)
        leds.setSpeed(params.speed)
        leds.setBrightness(params.brightness)
        leds.setAutoCycle(params.autoCycle)

        yield True
        while True:
            yield False


