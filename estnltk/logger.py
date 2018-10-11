import logging
import tqdm


class TqdmLoggingHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        self.format = logging.Formatter("%(levelname)s:%(filename)s:%(lineno)s: %(message)s").format
        super(self.__class__, self).__init__(level)

    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.tqdm.write(msg)
            self.flush()
        except Exception:
            self.handleError(record)


def _get_logger(level='INFO'):
    log = logging.getLogger()
    log.addHandler(TqdmLoggingHandler())
    log.setLevel(level)

    return log


class EstNltkLogger:
    logger = None

    def __init__(self, level):
        if self.__class__.logger is None:
            self.__class__.logger = _get_logger(level)


def get_logger(level='INFO'):
    return EstNltkLogger(level).logger
