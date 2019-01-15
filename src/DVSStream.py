
import numpy as np
import os
from .EventStream import EventStream
from .config import VERSION,TYPE

DVStype=[('x',np.uint16), ('y', np.uint16), ('isIncrease', np.bool_), ('timestamp', np.uint64)];

class DVSStream(EventStream):
    """
    """
    def __init__(self, _width, _height, _events, _version=VERSION):
        super().__init__(_events, DVStype, _version);
        self.width = np.uint16(_width);
        self.height = np.uint16(_height);

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
        to_write.append(TYPE['DVS']);
        to_write.append(np.uint8(self.width)); 
        to_write.append(np.uint8(self.width >> 8)); 
        to_write.append(np.uint8(self.height)); 
        to_write.append(np.uint8(self.height >> 8)); 
        
        previousTs = 0;
        for datum in self.data : 
            relativeTs = datum.ts - previousTs;
            if relativeTs > 127 :
                numberOfOverflows = int(relativeTs / 128);
                for i in range (numberOfOverflows):
                    to_write.append(0xff);
                relativeTs -= numberOfOverflows * 128;
            to_write.append(np.uint8( (np.uint8(relativeTs) < 1) | (datum.isIncrease & 0x01)));
            to_write.append(np.uint8( datum.x ));
            to_write.append(np.uint8( datum.x >> 8));
            to_write.append(np.uint8( datum.y ));
            to_write.append(np.uint8( datum.y >> 8));
            previousTs = datum.ts;
        ES_file = open(filename, 'wb');
        ES_file.write(to_write);
        ES_file.close();
