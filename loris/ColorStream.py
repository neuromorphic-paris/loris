
import numpy as np
import os
from .EventStream import EventStream
from .config import VERSION, TYPE

Colortype = [('x', np.uint16), ('y', np.uint8), ('r', np.uint8),
             ('g', np.uint8), ('b', np.uint8), ('ts', np.uint64)]


class ColorStream(EventStream):
    """
    """
    def __init__(self, _width, _height, _events, _version=VERSION):
        super.__init__(_events, Colortype, _version)
        self.width = np.uint16(_width)
        self.height = np.uint16(_height)

    def readColorStream(event_data, version):
        width = (event_data[17] << 8) + event_data[16]
        height = (event_data[19] << 8) + event_data[18]
        file_cursor = 20
        end = len(event_data)
        events = []
        currentTime = 0
        while(file_cursor < end):
            byte = event_data[file_cursor]
            if byte & 0xfe == 0xfe:
                if byte == 0xfe:  # Reset event
                    pass
                else:  # Overflow event
                    currentTime += 0xfe
            else:
                file_cursor += 1
                byte1 = event_data[file_cursor]
                file_cursor += 1
                byte2 = event_data[file_cursor]
                file_cursor += 1
                byte3 = event_data[file_cursor]
                file_cursor += 1
                byte4 = event_data[file_cursor]
                file_cursor += 1
                byte5 = event_data[file_cursor]
                file_cursor += 1
                byte6 = event_data[file_cursor]
                file_cursor += 1
                byte7 = event_data[file_cursor]
                currentTime += byte
                x = (byte2 << 8 | byte1)
                y = (byte4 << 8 | byte3)
                r = byte5
                g = byte6
                b = byte7
                events.append((x, y, r, g, b, currentTime))
            file_cursor += 1
        return ColorStream(width, height, events, version)

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
        to_write.append(self.version.split('.')[0])
        to_write.append(self.version.split('.')[1])
        to_write.append(self.version.split('.')[2])
        to_write.append(TYPE['Color'])
        to_write.append(np.uint8(self.width))
        to_write.append(np.uint8(self.width >> 8))
        to_write.append(np.uint8(self.height))
        to_write.append(np.uint8(self.height >> 8))
        previousTs = 0
        for datum in self.data:
            relativeTs = datum.ts - previousTs
            if relativeTs >= 254:
                numberOfOverflows = int(relativeTs / 255)
                for i in range(numberOfOverflows):
                    to_write.append(0xff)
                relativeTs -= numberOfOverflows * 254
            to_write.append(np.uint8(relativeTs))
            to_write.append(np.uint8(datum.x))
            to_write.append(np.uint8(datum.x >> 8))
            to_write.append(np.uint8(datum.y))
            to_write.append(np.uint8(datum.y >> 8))
            to_write.append(np.uint8(datum.r))
            to_write.append(np.uint8(datum.g))
            to_write.append(np.uint8(datum.b))
            previousTs = datum.ts
        ES_file = open(filename, 'wb')
        ES_file.write(to_write)
        ES_file.close()
