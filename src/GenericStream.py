import numpy as np
import os
from .EventStream import EventStream
from .config      import VERSION,TYPE

Generictype=[('data',np.int), ('ts', np.uint64)];

class GenericStream(EventStream):
    """
    """
    def __init__(self, _events, _version=VERSION):
        super().__init__(_events, Generictype, _version);

    def write(self, filename):
        """
        Warning this function is broken;
        """
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        to_write = bytearray('Event Stream','ascii');
        to_wrtie.append(self.version.split('.')[0]);
        to_wrtie.append(self.version.split('.')[1]);
        to_wrtie.append(self.version.split('.')[2]);
        to_write.append(TYPE['ATIS']);
        previousTs = 0;
        for datum in self.data : 
            relativeTs = datum.ts - previousTs;
            if relativeTs > 253:
                numberOfOverflows = int(relativeTs / 254);
                for i in range (numberOfOverflows):
                    to_write.append(0xff);
                relativeTs -= numberOfOverflows * 254;
            previousTs = datum.ts;
        ES_file = open(filename, 'wb');
        ES_file.write(to_write);
        ES_file.close();
