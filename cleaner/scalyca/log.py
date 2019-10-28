import logging
import time
from . import colour as c


class Formatter(logging.Formatter):
    def __init__(self):
        print("init")
        super().__init__('{asctime} [{levelname}] {message}', "%Y-%m-%d %H:%M:%S", '{')

    def format(self, record):
        return super().format(record)

    def formatTime(self, record, datefmt):
        ct = self.converter(record.created)
        return f"{datetime.strftime('%H:%M:%S', ct)}.{int(record.msecs):06d}"


def setupLog(name, *, output=None):
    print("Setting up log")
    formatter = Formatter()

    if type(output) == str:
        handler = logging.FileHandler(output)
    else:
        handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    log.addHandler(handler)

    return log
