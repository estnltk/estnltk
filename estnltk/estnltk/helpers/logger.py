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
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def get_logger_with_tqdm_handler(level=logging.INFO):
    # Check if a TqdmLoggingHandler is already attached
    if not any(isinstance(h, TqdmLoggingHandler) for h in logger.handlers):
        logger.addHandler(TqdmLoggingHandler())
        logger.setLevel(level)
    return logger

