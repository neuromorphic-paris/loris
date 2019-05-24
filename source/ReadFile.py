from . import EventStream as event_stream
from . import DAT as dat
from . import CSV as csv

is_using_fallback = False
try:
    import loris_extension
except ImportError:
    is_using_fallback = True
    print("Could not import c++ extension to speed up things. Falling back to pure Python implementation...")


def read_file(file_name):
    """parse a file from a neuromorphic camera and return events
    supported file formats are .aedat, .dat, .es and .csv
    """
    if file_name.endswith('.aedat'):
        print("Not yet implemented")
        return None
    # dat
    elif file_name.endswith('.dat') and is_using_fallback:
        parsed_file = dat.parse_file(file_name)
    elif file_name.endswith('.dat') and '_td' in file_name:
        parsed_file = loris_extension.read_dat_td(file_name)
    elif file_name.endswith('.dat') and '_aps' in file_name:
        parsed_file = loris_extension.read_dat_aps(file_name)
    # EventStream
    elif file_name.endswith('.es') and is_using_fallback:
        parsed_file = event_stream.parse_file(file_name)
    elif file_name.endswith('.es'):
        parsed_file = loris_extension.read_event_stream(file_name)
    # csv
    elif file_name.endswith('.csv'):
        parsed_file = csv.parse_file(file_name)
    else:
        print("I don't know what kind of format you want to read. "
              + "Please specify a valid file name ending such as .aedat etc")
        return None
    check_incoherent_events(parsed_file)
    return parsed_file

def check_incoherent_events(parsed_file):
    for i in range(0, len(parsed_file['events'])):
        if i > 0 and parsed_file['events']['t'][i-1] > parsed_file['events']['t'][i]:
            print('Not all timestamps are in ascending order, just so you know.')
            break
    return
