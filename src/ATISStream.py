import numpy as np
from tqdm import tqdm
import os
from .EventStream import EventStream
from .config import VERSION, TYPE

ATIStype = [('x', np.uint16), ('y', np.uint16),
            ('p', np.bool_), ('is_tc', np.bool_), ('ts', np.uint64)]


class ATISStream(EventStream):
    """
    """
    def __init__(self, _width, _height, _events, _version=VERSION):
        super().__init__(_events, ATIStype, _version)
        self.width = np.uint16(_width)
        self.height = np.uint16(_height)

    def read(event_data, version):
        width = (event_data[17] << 8) + event_data[16]
        height = (event_data[19] << 8) + event_data[18]
        file_cursor = 20
        end = len(event_data)
        events = []
        current_time = 0
        bar = tqdm(total=int(end), unit_scale=True, ncols=80, unit='Events')
        while(file_cursor < end):
            byte = event_data[file_cursor]
            if byte & 0xfc == 0xfc:
                if byte == 0xfc:  # Reset event
                    pass
                else:  # Overflow event
                    current_time += (byte & 0x03) * 63
            else:
                file_cursor += 1
                byte1 = event_data[file_cursor]
                file_cursor += 1
                byte2 = event_data[file_cursor]
                file_cursor += 1
                byte3 = event_data[file_cursor]
                file_cursor += 1
                byte4 = event_data[file_cursor]
                bar.update(4)
                current_time += (byte >> 2)
                x = ((byte2 << 8) | byte1)
                y = ((byte4 << 8) | byte3)
                is_tc = (byte & 0x01)
                p = ((byte & 0x02) >> 1)
                events.append((x, y, p, is_tc, current_time))
            file_cursor += 1
            bar.update(1)
        bar.close()
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
        previous_ts = 0
        bar_scale = 1000
        counter = 0
        bar = tqdm(total=self.data.size/bar_scale, unit_scale=True,
                   ncols=80, unit='kEvents')
        for datum in self.data:
            relative_ts = datum.ts - previous_ts
            if relative_ts >= 63:
                number_of_overflows = int(relative_ts / 63)
                relative_ts -= number_of_overflows * 63
                for i in range(int(number_of_overflows/3)):
                    to_write.append(0xff)
                number_of_overflows = number_of_overflows % 3
                if number_of_overflows > 0:
                    to_write.append(0xfc | np.uint8(number_of_overflows))
            to_write.append(np.uint8((np.uint8(relative_ts) << 2) & 0xfc)
                            | (datum.p << 1) | datum.is_tc)
            to_write.append(np.uint8(datum.x))
            to_write.append(np.uint8(datum.x >> 8))
            to_write.append(np.uint8(datum.y))
            to_write.append(np.uint8(datum.y >> 8))
            previous_ts = datum.ts
            counter += 1
            if counter % bar_scale == 0:
                bar.update(1)
        file = open(filename, 'wb')
        file.write(to_write)
        file.close()
        bar.close()
