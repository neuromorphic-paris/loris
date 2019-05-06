import numpy as np

# DAT
DATtype = [('ts', np.uint64), ('x', np.uint16), ('y', np.uint16), ('p', np.bool_)]

# ES
VERSION = '2.0.0'
TYPE = {
        'Generic': 0,
        'DVS': 1,
        'ATIS': 2,
        'AMD': 3,
        'Color': 4,
        }
REVTYPE = ['Generic', 'DVS', 'ATIS', 'AMD', 'Color']
Generictype = [('data', np.int), ('ts', np.uint64)]
DVStype = [('ts', np.uint64), ('x', np.uint16), ('y', np.uint16),
           ('is_increase', np.bool_)]
ATIStype = [('ts', np.uint64), ('x', np.uint16), ('y', np.uint16),
            ('p', np.bool_), ('is_tc', np.bool_)]
AMDtype = [('x', np.uint8), ('y', np.uint8), ('s', np.uint8), ('int', np.uint8), ('ts', np.uint64)]
Colortype = [('x', np.uint16), ('y', np.uint8), ('r', np.uint8),
             ('g', np.uint8), ('b', np.uint8), ('ts', np.uint64)]
