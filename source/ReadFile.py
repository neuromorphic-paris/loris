import loris_extension
from . import CSV as csv
import os
import numpy as np


def read_file(file_name, file_name_dat_aps=None, verbose=False):
    """parse a file from a neuromorphic camera and return events
    supported file formats are .aedat, .dat, .es and .csv
    """
    if file_name.endswith('.aedat'):
        print("Parsing the aedat file format is not implemented. Have a look at the dv-python package.")
        return None
    elif file_name.endswith('.dat') and '_aps' in file_name and file_name_dat_aps == None:
        parsed_file = loris_extension.read_dat_aps(file_name)
    elif file_name.endswith('.dat') and file_name_dat_aps != None and file_name_dat_aps.endswith('.dat'):
        parsed_file = loris_extension.read_dat_td_aps(file_name, file_name_dat_aps)
    elif file_name.endswith('.dat') and file_name_dat_aps == None:
        parsed_file = loris_extension.read_dat_td(file_name)
    elif file_name.endswith('.es'):
        parsed_file = loris_extension.read_event_stream(file_name)
    elif file_name.endswith('.csv'):
        parsed_file = csv.parse_file(file_name)
    else:
        print("I don't know what kind of format you want to read. "
              + "Please specify a valid file name ending such as .aedat etc")
        return None
    if parsed_file['type'] == 'dvs':
        parsed_file['events'] = parsed_file['events'].view(dtype=[(('ts', 't'), '<u8'), ('x', '<u2'),
                                                                  ('y', '<u2'), (('p', 'is_increase'), '?')])
    elif parsed_file['type'] == 'atis':
        parsed_file['events'] = parsed_file['events'].view(dtype=[(('ts', 't'), '<u8'), ('x', '<u2'),
                                                                  ('y', '<u2'), ('is_threshold_crossing', '?'),
                                                                  (('p', 'polarity'), '?')])
    parsed_file['events'] = parsed_file['events'].view(type=np.rec.recarray)
    if verbose and file_name_dat_aps == None:
        print("Read " + str(len(parsed_file['events'])) + " events of type " + parsed_file['type'] + " from " + os.path.split(file_name)[-1])
    elif verbose:
        print("Read " + str(len(parsed_file['events'])) + " events from combined files with dvs and atis events.")
    return parsed_file
