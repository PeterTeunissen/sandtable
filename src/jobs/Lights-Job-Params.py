from dialog import DialogInt
from dialog import DialogColor 
from dialog import DialogStr 
from dialog import DialogFile
from dialog import DialogTrueFalse
from dialog import DialogList
from jobable import Jobable
from Sand import MOVIE_SCRIPT_PATH, ledPatterns
import logging

class Jober(Jobable):
    def __init__(self):
        p = ledPatterns.copy()
        p.pop(0)
        logging.info("left over patterns %s" % p)
        self.editor = [
            DialogStr("name", "Job Name"),
            DialogColor("color", "Color", default=(255, 0, 0)),
            DialogList("modeStr", "Light Mode", list=p),
            DialogInt("speed", "Speed", default=9000, min=1, max=65535),
            DialogInt("brightness", "Brightness", default=50, min=1, max=255),
	        DialogTrueFalse("autoCycle", "Auto Cycle", default=False),
            DialogStr("cron", "Cron Expression")
        ]

