from dialog import DialogInt
from dialog import DialogColor 
from dialog import DialogStr 
from dialog import DialogFile
from dialog import DialogTrueFalse
from jobable import Jobable
from Sand import MOVIE_SCRIPT_PATH

class Jober(Jobable):
    def __init__(self):
        self.editor = [
            DialogStr("name", "Job Name"),
            DialogFile("filename", "File Name",  default=MOVIE_SCRIPT_PATH, filter='.xml'),
            DialogStr("job", "Job Type"),
            DialogStr("params", "Job Params"),
            DialogStr("cron", "Cron Expression")
        ]

