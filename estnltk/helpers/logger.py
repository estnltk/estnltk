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
            # self.flush()
        except Exception:
            self.handleError(record)


logger = logging.getLogger()
logger.addHandler(TqdmLoggingHandler())
logger.setLevel('INFO')
