import loris_extension
from .utils import guess_event_ordering
from numpy.lib import recfunctions as rfn
import numpy as np


def write_events_to_file(event_structure, output_file_name, ordering=None, verbose=False):
    """store a structured numpy array of events to a given file format
    supported file format is .es
    """
    res = None
    if output_file_name.endswith('.es'):
        if isinstance(event_structure, dict) and all(key in ['type', 'width', 'height', 'events'] for key in event_structure):
            res = loris_extension.write_event_stream(event_structure, output_file_name)
            if verbose: print("Wrote " + str(len(event_structure['events'])) + " events of type " + event_structure['type'] + " to " + output_file_name)
        else:
            if len(event_structure.dtype.descr) == 1:
                if ordering == None: ordering = guess_event_ordering(event_structure)
                x_index = ordering.find("x")
                y_index = ordering.find("y")
                t_index = ordering.find("t")
                p_index = ordering.find("p")
                permutation = [t_index, x_index, y_index, p_index]
                event_structure = event_structure[:, permutation]
                if len(ordering) == 4:
                    dt = np.dtype([('t', '<u8'), ('x', '<u2'), ('y', '<u2'), ('is_increase', '?')])
                    event_type = 'dvs'
                elif len(ordering) == 5:
                    np.dtype([('t', '<u8'), ('x', '<u2'), ('y', '<u2'), ('is_threshold_crossing', '?'), ('is_increase', '?')])
                    event_type = 'atis'
                events = rfn.unstructured_to_structured(event_structure, dt)
                width = int(max(event_structure[:,x_index])+1)
                height = int(max(event_structure[:,y_index])+1)
                file_dict = {'type': event_type, 'width': width, 'height': height, 'events': events}
                res = loris_extension.write_event_stream(file_dict, output_file_name)
            else:
                width = int(max(event_structure['x'])+1)
                height = int(max(event_structure['y'])+1)
                event_type = 'dvs' if len(event_structure.dtype) == 4 else 'atis' if len(event_structure.dtype) == 5 else 'unknown'
                file_dict = {'type': event_type, 'width': width, 'height': height, 'events': event_structure}
                res = loris_extension.write_event_stream(file_dict, output_file_name)
                if verbose: print("Wrote " + str(len(event_structure)) + " events of type " + event_type + " to " + output_file_name)
    elif output_file_name.endswith('.dat'):
        print("This is not implemented.")
    elif output_file_name.endswith('.aedat'):
        print("This is not implemented.")
    else:
        print("I don't know what kind of format you want to write to. "
              + "Please specify a valid file name ending such as .es")
    return res
