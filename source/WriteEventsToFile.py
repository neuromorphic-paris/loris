import loris_extension


def write_events_to_file(parsed_file, output_file_name, verbose=False):
    """store a structured numpy array of events to a given file format
    supported file format is .es
    """
    res = None
    if output_file_name.endswith('.es'):
        if isinstance(parsed_file, dict) and all(key in ['type', 'width', 'height', 'events'] for key in parsed_file):
            res = loris_extension.write_event_stream(parsed_file, output_file_name)
            if verbose:
                print("Wrote " + str(len(parsed_file['events'])) + " events of type " + parsed_file['type'] + " to " + output_file_name)
        else:
            width = int(max(parsed_file['x'])+1)
            height = int(max(parsed_file['y'])+1)
            event_type = 'dvs' if len(parsed_file.dtype) == 4 else 'atis' if len(parsed_file.dtype) == 5 else 'unknown'
            file_dict = {'type': event_type, 'width': width, 'height': height, 'events': parsed_file}
            res = loris_extension.write_event_stream(file_dict, output_file_name)
            if verbose:
                print("Wrote " + str(len(parsed_file)) + " events of type " + event_type + " to " + output_file_name)
    elif output_file_name.endswith('.dat'):
        print("This is not implemented.")
    elif output_file_name.endswith('.aedat'):
        print("This is not implemented.")
    else:
        print("I don't know what kind of format you want to write to. "
              + "Please specify a valid file name ending such as .es")
    return res
