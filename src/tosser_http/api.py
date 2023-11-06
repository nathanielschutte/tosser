import os
from tosser import Tosser

BASE_WORKDIR = os.path.abspath(os.path.dirname(__file__)) + '/workspace'

class TosserApi():
    def __init__(self) -> None:
        self.tosser = Tosser()
        self.tosser.set_work_dir(BASE_WORKDIR)
