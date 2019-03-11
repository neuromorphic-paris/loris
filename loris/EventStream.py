import os
import numpy as np
from tqdm.auto import tqdm
from . import config


"""read and write events in the Event Stream format
"""
def parse_file(file_name):
    event_file = open(file_name, 'rb')
    event_data = event_file.read()
    event_file.close()
    if event_data[0:12] != b'Event Stream':
        print("This does not look like an .es file. Aborting.")
        return event_data[0:12]
    stream_version_major = event_data[12]
    stream_version_minor = event_data[13]
    stream_version_patch = event_data[14]
    stream_version = str(stream_version_major) + '.'\
        + str(stream_version_minor) + '.'\
        + str(stream_version_patch)
    if stream_version_major is not 2:
        print("Only version 2 of EventStream format supported.")
        return None
    stream_type = event_data[15]
    print("reading " + config.REVTYPE[stream_type] + " EventStream file version "
          + stream_version)
    width = (event_data[17] << 8) + event_data[16]
    height = (event_data[19] << 8) + event_data[18]
    file_cursor = 20
    end = len(event_data)
    events = []
    current_time = 0
    bar = tqdm(total=int(end), unit_scale=True, ncols=80, unit='Events')
    if stream_type is 0:
        return parse_generic_data(event_data, stream_version)
    elif stream_type is 1:
        return parse_dvs_data(event_data, stream_version, width, height, file_cursor, end, events, current_time, bar)
    elif stream_type is 2:
        return parse_atis_data(event_data, stream_version, width, height, file_cursor, end, events, current_time, bar)
    elif stream_type is 3:
        return parse_amd_data(event_data, stream_version)
    elif stream_type is 4:
        return parse_color_data(event_data, stream_version)
    else:
        return None

def write_file(events, output_file_name, width, height):
    if not os.path.exists(os.path.dirname(output_file_name)):
        try:
            os.makedirs(os.path.dirname(output_file_name))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    to_write = bytearray('Event Stream', 'ascii')
    to_write.append(int(config.VERSION.split('.')[0]))
    to_write.append(int(config.VERSION.split('.')[1]))
    to_write.append(int(config.VERSION.split('.')[2]))
    previous_ts = 0
    bar_scale = 1000
    counter = 0
    bar = tqdm(total=len(events)/bar_scale, unit_scale=True,
               ncols=80, unit='kEvents')
    if 'is_tc' in events.dtype.names:
        print("detected ATIS events")
        return write_atis_file(events, output_file_name, to_write, previous_ts, bar_scale, counter, bar, width, height)
    elif 'is_increase' in events.dtype.names:
        print("detected DVS events")
        return write_dvs_file(events, output_file_name, to_write, previous_ts, bar_scale, counter, bar, width, height)
    else:
        print("Not sure which type of events are encoded here.")
        return None

def parse_dvs_data(event_data, version, width, height, file_cursor, end, events, current_time, bar):
    while(file_cursor < end):
        byte = event_data[file_cursor]
        if byte & 0xfe == 0xfe:
            if byte == 0xfe:  # Reset event
                pass
            else:  # Overflow event
                current_time += 127
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
            current_time += (byte >> 1)
            x = ((byte2 << 8) | byte1)
            y = ((byte4 << 8) | byte3)
            is_increase = (byte & 0x01)
            events.append((current_time, x, y, is_increase))
        file_cursor += 1
        bar.update(1)
    bar.close()
    return np.array(events, dtype=config.DVStype) # , width, height

def write_dvs_file(events, output_file_name, to_write, previous_ts, bar_scale, counter, bar, width, height):
    to_write.append(config.TYPE['DVS'])
    if width is 0:
        width = max(events['x']) + 1
        height = max(events['y']) + 1
    to_write.append(np.uint8(width))
    to_write.append(np.uint8(width >> 8))
    to_write.append(np.uint8(height))
    to_write.append(np.uint8(height >> 8))
    for event in events:
        relative_ts = event[0] - previous_ts
        if relative_ts >= 127:
            number_of_overflows = int(relative_ts / 127)
            for i in range(number_of_overflows):
                to_write.append(0xff)
            relative_ts -= number_of_overflows * 127
        to_write.append(np.uint8((np.uint8(relative_ts) << 1)
                        | (event[3] & 0x01)))
        to_write.append(np.uint8(event[1]))
        to_write.append(np.uint8(event[1] >> 8))
        to_write.append(np.uint8(event[2]))
        to_write.append(np.uint8(event[2] >> 8))
        previous_ts = event[0]
        counter += 1
        if counter % bar_scale == 0:
            bar.update(1)
    file = open(output_file_name, 'wb')
    file.write(to_write)
    file.close()
    bar.close()

def parse_atis_data(event_data, version, width, height, file_cursor, end, events, current_time, bar):
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
            events.append((current_time, x, y, p, is_tc))
        file_cursor += 1
        bar.update(1)
    bar.close()
    return np.array(events, dtype=config.ATIStype), width, height

def write_atis_file(events, output_file_name, to_write, previous_ts, bar_scale, counter, bar, width, height):
    to_write.append(config.TYPE['ATIS'])
    if width is 0:
        width = max(events['x']) + 1
        height = max(events['y']) + 1
    to_write.append(np.uint8(width))
    to_write.append(np.uint8(width >> 8))
    to_write.append(np.uint8(height))
    to_write.append(np.uint8(height >> 8))
    for event in events:
        relative_ts = event[0] - previous_ts
        if relative_ts >= 63:
            number_of_overflows = int(relative_ts / 63)
            relative_ts -= number_of_overflows * 63
            for i in range(int(number_of_overflows/3)):
                to_write.append(0xff)
            number_of_overflows = number_of_overflows % 3
            if number_of_overflows > 0:
                to_write.append(0xfc | np.uint8(number_of_overflows))
        to_write.append(np.uint8((np.uint8(relative_ts) << 2) & 0xfc)
                        | (event[3] << 1) | event[4])
        to_write.append(np.uint8(event[1]))
        to_write.append(np.uint8(event[1] >> 8))
        to_write.append(np.uint8(event[2]))
        to_write.append(np.uint8(event[2] >> 8))
        previous_ts = event[0]
        counter += 1
        if counter % bar_scale == 0:
            bar.update(1)
    file = open(output_file_name, 'wb')
    file.write(to_write)
    file.close()
    bar.close()

def parse_generic_data(event_data):
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

def write_generic_file(self, output_file_name):
    """
    Warning this function is broken;
    """
    if not os.path.exists(os.path.dirname(output_file_name)):
        try:
            os.makedirs(os.path.dirname(output_file_name))
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
    ES_file = open(output_file_name, 'wb')
    ES_file.write(to_write)
    ES_file.close()

def parse_amd_data(event_data):
    f_cursor = 16
    end = len(event_data)
    events = []
    currentTime = 0
    while(f_cursor < end):
        byte = event_data[f_cursor]
        if byte & 0xfe == 0xfe:
            if byte == 0xfe:  # Reset event
                pass
            else:  # Overflow event
                currentTime += 0xfe

        else:
            f_cursor += 1
            byte1 = ESdate[f_cursor]
            f_cursor += 1
            byte2 = ESfile[f_cursor]
            f_cursor += 1
            byte3 = ESfile[f_cursor]
            currentTime += byte
            x = byte1
            y = byte2
            s = byte3
            events.append((x, y, s, currentTime))
        f_cursor += 1
    return AMDStream(events, version)

def write_amd_file(self, output_file_name):
    """
    """
    if not os.path.exists(os.path.dirname(output_file_name)):
        try:
            os.makedirs(os.path.dirname(output_file_name))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    to_write = bytearray('Event Stream', 'ascii')
    to_write.append(self.version.split('.')[0])
    to_write.append(self.version.split('.')[1])
    to_write.append(self.version.split('.')[2])
    to_write.append(TYPE['AMD'])
    previousTs = 0
    for datum in self.data:
        relativeTs = datum.ts - previousTs
        if relativeTs > 253:
            numberOfOverflows = int(relativeTs / 254)
            for i in range(numberOfOverflows):
                to_write.append(0xff)
            relativeTs -= numberOfOverflows * 254
        to_write.append(np.uint8(relativeTs))
        to_write.append(np.uint8(datum.x))
        to_write.append(np.uint8(datum.y))
        to_write.append(np.uint8(datum.s))
        previousTs = datum.ts
    ES_file = open(output_file_name, 'wb')
    ES_file.write(to_write)
    ES_file.close()

def parse_color_data(event_data, version):
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

def write_color_file(self, output_file_name):
    """
    """
    if not os.path.exists(os.path.dirname(output_file_name)):
        try:
            os.makedirs(os.path.dirname(output_file_name))
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
    ES_file = open(output_file_name, 'wb')
    ES_file.write(to_write)
    ES_file.close()
