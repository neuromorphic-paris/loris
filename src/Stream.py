
import numpy as np
import os
from .config import VERSION


class Stream(object):
    """
    Base Class for a Stream 
    """
    def __init__(self, _events, _dtype, _version=VERSION):
        self.data       = np.rec.array(_events,dtype = _dtype);
        self.version    = _version;

    def order(self):
        self.data.sort(order='ts');

    def write(self, filename):
        """
        """
        print('Error: the method need to be overwrite by the child');
