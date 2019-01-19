from .DVSStream import DVSStream
from .ATISStream import ATISStream
from .AMDStream import AMDStream
from .ColorStream import ColorStream
from .GenericStream import GenericStream
from .readtddat import readATIS_td_better
from .config import REVTYPE

"""parse a file from a neuromorphic camera and return events

supported file formats are .dat, .aedat and .es
"""
def read_file(file_name):
    event_file = open(file_name, 'rb')
    event_data = event_file.read()
    event_file.close()
    if file_name.endswith('.es') and event_data[0:12] == b'Event Stream':
        return EventStream.parse_file(event_data)
    elif file_name.endswith('.dat'):  # and event_data[0:11] == b'% Data file':
        return DAT.parse_file(event_data)
    elif file_name.endswith('.aedat'):
        print("Not yet implemented")
        return None
    else:
        print("File format not supported, returning null. It is highly likely "
        + "that it is straightforward to include your file's version to loris. "
        + "Please submit an issue on Github, thanks!")
        return None
