import logging
import time
from . import colour as c


class Formatter(logging.Formatter):
    def __init__(self):
        super().__init__('{asctime} [{level}] {message}', "%Y-%m-%d %H:%M:%S", '{')

    def format(self, record):
        record.level = {
            'DEBUG':    c.debug,
            'INFO':     c.none,
            'WARNING':  c.warn,
            'ERROR':    c.err,
            'CRITICAL': c.critical,
        }[record.levelname](record.levelname[:3])

        return super().format(record)

    def formatTime(self, record, format):
        ct = self.converter(record.created)
        return f"{time.strftime('%Y-%m-%d %H:%M:%S', ct)}.{int(record.msecs):03d}"


def setupLog(name, *, output=None):
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
