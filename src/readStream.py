from .DVSStream import DVSStream;
from .ATISStream import ATISStream;
from .AMDStream import AMDStream;
from .ColorStream import ColorStream;
from .GenericStream import GenericStream;
#from .tools import FormatError;

def readStream(filename):
    event_file = open(filename, 'rb')
    event_data = event_file.read()
    event_file.close()
    if event_data[0:12] != b'Event Stream':
        print("This is not an EventStream file, returning null")
        #´TODO read .dat files
        return None

    stream_version_major = event_data[12]
    stream_version_minor = event_data[13]
    stream_version_patch = event_data[14]
    stream_version = str(stream_version_major) + '.' + str(stream_version_minor) + '.' + str(stream_version_patch)
    if stream_version_major is not 2:
        print("Only version 2 of EventStream format supported.")
        return None

    stream_type = event_data[15]

    print("reading EventStream file version " + stream_version + ", type " + str(stream_type))

    if stream_type is 0:
        return GenericStream.read(event_data, stream_version)
    elif stream_type is 1:
        return DVSStream.read(event_data, stream_version)
    elif stream_type is 2:
        return ATISStream.read(event_data, stream_version)
    elif stream_type is 3:
        return AMDStream.read(event_data, stream_version)
    elif stream_type is 4:
        return ColorStream.read(event_data, stream_version)
    else:
        return None
