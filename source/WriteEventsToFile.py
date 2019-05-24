import loris_extension


def write_events_to_file(parsed_file, output_file_name):
    """store a structured numpy array of events to a given file format
    supported file format is .es
    """
    res = None
    if output_file_name.endswith('.es'):
        res = loris_extension.write_event_stream(parsed_file, output_file_name)
        print("Wrote " + str(len(parsed_file['events'])) + " events of type " + parsed_file['type'] + " to " + output_file_name)
    elif output_file_name.endswith('.dat'):
        print("This is not implemented.")
    elif output_file_name.endswith('.aedat'):
        print("This is not implemented.")
    else:
        print("I don't know what kind of format you want to write to. "
              + "Please specify a valid file name ending such as .es")
    return res
