import numpy as np
import os
from .EventStream import EventStream
from .config import VERSION, TYPE

Generictype = [('data', np.int), ('ts', np.uint64)]


class GenericStream(EventStream):
    """
    """
    def __init__(self, _events, _version=VERSION):
        super().__init__(_events, Generictype, _version)

    def return_test_string():
        print("generic middle")
        return "generic test"

    def read(event_data):
        f_cursor = 15
        events = []
        currentTime = 0
        end = len(event_data)
        while(f_cursor < end):
            byte = event_data[f_cursor]
            if byte & 0xfe == 0xfe:
                if byte == 0xfe:  # Reset event
                    pass
                else:  # Overflow event
                    currentTime += 0xfe
            else:
                currentTime += byte
                is_last = False
                size = 0
                i = 0
                while (not is_last):
                    f_cursor += 1
                    byte = event_data[f_cursor]
                    is_last = True * (byte & 0x01)
                    size += (byte >> 1) << (7 * i)
                    i += 1
                data = 0
                k = 0
                for j in range(i):
                    f_cursor += 1
                    byte = event_data[f_cursor]
                    data += byte << (7*k)
                    k += 1
                events.append((data, currentTime))
            f_cursor += 1
        return GenericStream(events, version)

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

        to_write = bytearray('Event Stream', 'ascii')
        to_write.append(self.version.split('.')[0])
        to_write.append(self.version.split('.')[1])
        to_write.append(self.version.split('.')[2])
        to_write.append(TYPE['ATIS'])
        previousTs = 0
        for datum in self.data:
            relativeTs = datum.ts - previousTs
            if relativeTs > 253:
                numberOfOverflows = int(relativeTs / 254)
                for i in range(numberOfOverflows):
                    to_write.append(0xff)
                relativeTs -= numberOfOverflows * 254
            previousTs = datum.ts
        ES_file = open(filename, 'wb')
        ES_file.write(to_write)
        ES_file.close()
