from tqdm import tqdm
from tqdm.notebook import tqdm as notebook_tqdm

class Progressbar:
    def __init__(self, iterable, total, initial, progressbar_type):
        self.progressbar_type = progressbar_type

        if progressbar_type is None:
            self.data_iterator = iterable
        elif progressbar_type in {'ascii', 'unicode'}:
            self.data_iterator = tqdm(iterable,
                                      total=total,
                                      initial=initial,
                                      unit='doc',
                                      ascii=progressbar_type == 'ascii',
                                      smoothing=0)
        elif progressbar_type == 'notebook':
            self.data_iterator = notebook_tqdm(iterable,
                                               total=total,
                                               initial=initial,
                                               unit='doc',
                                               smoothing=0)
        else:
            raise ValueError("unknown progressbar type: {!r}, expected None, 'ascii', 'unicode' or 'notebook'"
                             .format(progressbar_type))

    def set_description(self, description, refresh=False):
        if self.progressbar_type is not None:
            self.data_iterator.set_description(description, refresh=refresh)

    def __iter__(self):
        yield from self.data_iterator
