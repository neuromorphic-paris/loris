
import numpy as np
import os
from .EventStream import EventStream
from .config import VERSION, TYPE

ATIStype = [('x',np.uint16), ('y', np.uint16),
            ('p', np.bool_), ('isTc', np.bool_), ('ts', np.uint64)]


class ATISStream(EventStream):
    """
    """
    def __init__(self, _width, _height, _events, _version=VERSION):
        super().__init__(_events, ATIStype, _version)
        self.width = np.uint16(_width)
        self.height = np.uint16(_height)

    def read(event_data):
        width = event_data[17] << 8 + event_data[16]
        height = event_data[19] << 8 + event_data[18]
        f_cursor = 20
        end = len(event_data)
        events = []
        currentTime = 0
        while(f_cursor < end):
            byte = event_data[f_cursor]
            if byte & 0xfc == 0xfc:
                if byte == 0xfc:  # Reset event
                    pass
                else:  # Overflow event
                    currentTime += (byte & 0x03) * 64

            else:
                f_cursor += 1
                byte1 = ESdate[f_cursor]
                f_cursor += 1
                byte2 = ESfile[f_cursor]
                f_cursor += 1
                byte3 = ESfile[f_cursor]
                f_cursor += 1
                byte4 = ESfile[f_cursor]
                currentTime += (byte >> 2)
                x = ((byte2 << 8) | byte1)
                y = ((byte4 << 8) | byte3)
                isTc = (byte & 0x01)
                p = ((byte & 0x02) >> 1)
                events.append((x, y, p, isTc, currentTime))
            f_cursor += 1
        return ATISStream(width, height, events, version)

    def write(self, filename):
        """
        """
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        to_write = bytearray('Event Stream', 'ascii')
        to_write.append(int(self.version.split('.')[0]))
        to_write.append(int(self.version.split('.')[1]))
        to_write.append(int(self.version.split('.')[2]))
        to_write.append(TYPE['ATIS'])
        to_write.append(np.uint8(self.width))
        to_write.append(np.uint8(self.width >> 8))
        to_write.append(np.uint8(self.height))
        to_write.append(np.uint8(self.height >> 8))
        previousTs = 0
        for datum in self.data:
            relativeTs = datum.ts - previousTs
            if relativeTs > 63:
                numberOfOverflows = int(relativeTs / 64)
                for i in range(int(numberOfOverflows/3)):
                    to_write.append(0xff)
                numberOfOverflowsLeft = numberOfOverflows % 3
                if numberOfOverflowsLeft > 0:
                    to_write.append(0xfc | np.uint8(numberOfOverflowsLeft))
                relativeTs -= numberOfOverflows * 64
            to_write.append(np.uint8((relativeTs << 2) & 0xfc)
                            | (datum.p << 1) | (datum.isTc))
            to_write.append(np.uint8(datum.x))
            to_write.append(np.uint8(datum.x >> 8))
            to_write.append(np.uint8(datum.y))
            to_write.append(np.uint8(datum.y >> 8))
            previousTs = datum.ts
        ES_file = open(filename, 'wb')
        ES_file.write(to_write)
        ES_file.close()
