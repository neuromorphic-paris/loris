from . import EventStream as event_stream
from . import DAT as dat

def write_events_to_file(events, output_file_name, width=0, height=0):
    """store a structured numpy array of events to a given file format
    supported file formats are .dat, .aedat and .es
    """
    if output_file_name.endswith('.es'):
        return event_stream.write_file(events, output_file_name, width, height)
    elif output_file_name.endswith('.dat'):
        return dat.write_file(events, output_file_name)
    elif output_file_name.endswith('.aedat'):
        print("Not yet implemented")
        return None
    else:
        print("I don't know what kind of format you want to write to. "
              + "Please specify a valid file name ending such as .aedat etc")
        return None