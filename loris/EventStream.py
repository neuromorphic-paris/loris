import numpy as np
from .config import VERSION


class EventStream(object):
    """
    Base Class for an event stream
    """
    def __init__(self, _events, _dtype, _version=VERSION):
        self.data = np.rec.array(_events, dtype=_dtype)
        self.version = _version

    def order(self):
        self.data.sort(order='ts')

    def write(self, filename):
        """
        """
        print('Error: the method need to be overwrite by the child')
