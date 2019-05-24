import loris_extension


def write_events_to_file(events, output_file_name, width=0, height=0):
    """store a structured numpy array of events to a given file format
    supported file formats are .aedat, .dat and .es
    """
    if output_file_name.endswith('.es'):
        return loris_extension.write_event_stream(events, output_file_name)
    elif output_file_name.endswith('.dat'):
        print("This is not implemented.")
        return None
    elif output_file_name.endswith('.aedat'):
        print("This is not implemented.")
        return None
    else:
        print("I don't know what kind of format you want to write to. "
              + "Please specify a valid file name ending such as .es")
        return None
