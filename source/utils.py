import warnings
import numpy as np


def guess_event_ordering(events):
    """
    Guesses the names of the channels for events or returns numpy ndarray names

    Arguments:
    - events - the events in [num_events, channels]

    Returns:
    - guess - string representation of ordering of channels
    """

    warnings.warn("[Loris]::Guessing the ordering of events")

    if np.issubdtype(events.dtype, np.number):
        if events.shape[1] == 3:
            guess = "txp"
        elif events.shape[1] == 4:
            guess = "txyp"
        elif events.shape[1] == 5:
            guess = "txyzp"
    elif isinstance(events, (np.ndarray, np.generic)):
        guess = events.dtype.names
    else:
        raise NotImplementedError("Unable to guess event ordering")

    warnings.warn("[Loris]::Guessed [%s] as ordering of events" % guess)

    return guess
