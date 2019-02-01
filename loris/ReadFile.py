from . import EventStream as event_stream
from . import DAT as dat
from . import CSV as csv


def read_file(file_name):
    """parse a file from a neuromorphic camera and return events
    supported file formats are .aedat, .dat, .es and .csv
    """
    if file_name.endswith('.aedat'):
        print("Not yet implemented")
        return None
    elif file_name.endswith('.dat'):
        return dat.parse_file(file_name)
    elif file_name.endswith('.es'):
        return event_stream.parse_file(file_name)
    elif file_name.endswith('.csv'):
        return csv.parse_file(file_name)
    else:
        print("I don't know what kind of format you want to read. "
              + "Please specify a valid file name ending such as .aedat etc")
        return None
