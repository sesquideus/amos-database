import logging
import time
import colour as c


class Formatter(logging.Formatter):
    def __init__(self):
        super().__init__('{asctime} [{levelname}] {message}', "%H:%M:%S", '{')

    def format(self, record):
        record.levelname = {
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


def setupLog(name, *, stdout = True, outputFile = None):
    log = logging.getLogger(name)

    if stdout:
        handler = logging.StreamHandler()
        handler.setFormatter(Formatter())
        log.addHandler(handler)

    if outputFile is not None:
        handler = logging.FileHandler(outputFile)
        handler.setFormatter(Formatter())
        log.addHandler(handler)

    log.setLevel(logging.INFO)

    return log
