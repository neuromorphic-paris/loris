
import numpy as np
import os
from .EventStream import EventStream
from .config      import VERSION, TYPE

AMDtype=[('x',np.uint8), ('y', np.uint8), ('s', np.uint8), ('int', np.uint8), ('ts', np.uint64)]

class AMDStream(Stream):
    """
    """
    def __init__(self, _events, _version=VERSION):
        super().__init__(_events, AMDtype, _version);

    def write(self, filename):
        """
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
        to_write.append(TYPE['AMD']);
        previousTs = 0;
        for datum in self.data : 
            relativeTs = datum.ts - previousTs;
            if relativeTs > 253:
                numberOfOverflows = int(relativeTs / 254);
                for i in range (numberOfOverflows):
                    to_write.append(0xff);
                relativeTs -= numberOfOverflows * 254;
            to_write.append(np.uint8(relativeTs));
            to_write.append(np.uint8(datum.x));
            to_write.append(np.uint8(datum.y));
            to_write.append(np.uint8(datum.s));
            previousTs = datum.ts;
        ES_file = open(filename, 'wb');
        ES_file.write(to_write);
        ES_file.close();
