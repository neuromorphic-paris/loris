import os
import csv
import numpy as np
from tqdm.auto import tqdm


def parse_file(file_name):
    with open(file_name) as csvfile:
        print("parsing csv file...")
        reader = csv.reader(csvfile)
        lines = sum(1 for line in reader)
        bar = tqdm(total=lines, unit_scale=True, ncols=80, unit='Events')
        csvfile.seek(1)
        events = []
        first_event = next(reader)
        print(type(first_event[0]))
        if type(first_event[0]) is str:
            print("skipping first line...")
            first_event = next(reader)
        event_length = len(first_event)
        max_x = 0
        max_y = 0

        if event_length == 4:
            print("Assuming classic DVS event (t, x, y, p)")
            events.append((first_event[0], first_event[1], first_event[2], first_event[3]))
            for row in reader:
                events.append((row[0], row[1], row[2], row[3]))
                if int(row[1]) > max_x:
                    max_x = int(row[1])
                if int(row[2]) > max_y:
                    max_y = int(row[2])
                bar.update(1)
            bar.close()
            return {'type': 'dvs', 'width':max_x+1, 'height':max_y+1, \
                'events':np.array(events, dtype=[('t', np.uint64), ('x', np.uint16), ('y', np.uint16), ('is_increase', np.bool_)])}
        else:
            print("Sorry, I do not understand more than 4 event properties")
            return None
