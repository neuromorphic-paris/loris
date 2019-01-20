from . import EventStream as event_stream
from . import DAT as dat


def read_file(file_name):
    """parse a file from a neuromorphic camera and return events
    supported file formats are .dat, .aedat and .es
    """
    event_file = open(file_name, 'rb')
    event_data = event_file.read()
    event_file.close()
    if file_name.endswith('.es') and event_data[0:12] == b'Event Stream':
        return event_stream.parse_file(event_data)
    elif file_name.endswith('.dat'):  # and event_data[0:11] == b'% Data file':
        return dat.parse_file(event_data)
    elif file_name.endswith('.aedat'):
        print("Not yet implemented")
        return None
    else:
        print("File format not supported, returning null. It is highly likely "
        + "that it is straightforward to include your file's version to loris. "
        + "Please submit an issue on Github, thanks!")
        return None
