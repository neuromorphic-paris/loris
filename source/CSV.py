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
        event_length = len(first_event)
        if event_length == 3:
            print("Assuming Celex-5 Event Address Only Mode (x, y, t); no polarity")
            base_timestamp = 0
            lock = False
            events.append((int(first_event[2]), first_event[1], first_event[0], True))
            for row in reader:
                t = int(row[2])
                if t == 1499 and lock == False:
                    base_timestamp += 1500
                    time = 0 + base_timestamp
                    lock = True
                elif t == 1499 and lock == True:
                    time = 0 + base_timestamp
                elif t > 1500 or t < 0:
                    raise Exception('Not accepting timestamp ' + str(t))
                elif t < 1499:
                    time = t + base_timestamp
                    lock = False
                else:
                    pass
                events.append((time, row[0], row[1]))
                bar.update(1)
            bar.close()
            return np.array(events, dtype=[('t', np.uint64), ('x', np.uint16), ('y', np.uint16)])
        if event_length == 4:
            print("Assuming classic DVS event (x, y, p, t)")
            events.append((first_event[0], first_event[1], first_event[2], first_event[3]))
            for row in reader:
                events.append((row[0], row[1], row[2], row[3]))
                bar.update(1)
            bar.close()
            return np.array(events, dtype=[('t', np.uint64), ('x', np.uint16), ('y', np.uint16), ('is_increase', np.bool_)])
