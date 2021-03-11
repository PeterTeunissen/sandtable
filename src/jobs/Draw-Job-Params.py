from dialog import DialogInt
from dialog import DialogColor 
from dialog import DialogStr 
from dialog import DialogFile
from dialog import DialogOnOff
from dialog import DialogTrueFalse
from jobable import Jobable
from Sand import GCODE_PATH

class Jober(Jobable):
    def __init__(self):
        self.editor = [
            DialogStr("name", "Job Name"),
            DialogFile("filename", "File Name",  default=GCODE_PATH, filter='.gcode'),
            DialogTrueFalse("randomizeFile", "Random Drawing?", default=False),
            DialogStr("cron", "Cron Expression")
        ]

