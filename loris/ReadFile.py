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
        events = dat.parse_file(file_name)
    elif file_name.endswith('.es'):
        events = event_stream.parse_file(file_name)
    elif file_name.endswith('.csv'):
        events = csv.parse_file(file_name)
    else:
        print("I don't know what kind of format you want to read. "
              + "Please specify a valid file name ending such as .aedat etc")
        return None
    check_incoherent_events(events)
    return events

def check_incoherent_events(events):
    indices = []
    for index, event in enumerate(events):
        if index > 0 and events['ts'][index] < events['ts'][index-1]:
            indices.append(index)
            #print("Timestamp index - 1: "+ str(index-1) + ", index: " + str(index))
    if len(indices) == 0:
        print("All timestamps in correct order.")
    else:
        print("Not all timestamps are in ascending order.")
    return
