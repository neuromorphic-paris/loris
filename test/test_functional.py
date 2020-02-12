import unittest
import loris
import numpy as np
import os
from utils import create_random_input_with_ordering

examples_path_es = 'third_party/command_line_tools/third_party/sepia/third_party/event_stream/examples/'
examples_path_dat = 'test/example-files/'

class TestFunctionalAPI(unittest.TestCase):
    def setUp(self):
        self.event_array_txyp, self.sensor_size, self.ordering_txyp = create_random_input_with_ordering("txyp")
        self.event_array_xytp, self.sensor_size, self.ordering_xytp = create_random_input_with_ordering("xytp")

    def test_read_es_atis(self):
        file_atis = loris.read_file(examples_path_es + 'atis.es')
        self.assertEqual(1326017, len(file_atis['events']))
        self.assertEqual('atis', file_atis['type'])

    def test_read_es_color(self):
        file_color = loris.read_file(examples_path_es + 'color.es')
        self.assertEqual(473225, len(file_color['events']))
        self.assertEqual('color', file_color['type'])

    def test_read_es_dvs(self):
        file_dvs = loris.read_file(examples_path_es + 'dvs.es')
        self.assertEqual(473225, len(file_dvs['events']))
        self.assertEqual('dvs', file_dvs['type'])

    def test_read_es_generic(self):
        file_generic = loris.read_file(examples_path_es + 'generic.es')
        self.assertEqual(70, len(file_generic['events']))
        self.assertEqual('generic', file_generic['type'])

    def test_write_es_atis(self):
        file_atis = loris.read_file(examples_path_es + 'atis.es')
        new_file = 'new_atis.es'
        loris.write_events_to_file(file_atis, new_file)
        self.assertEqual(os.path.getsize(new_file), os.path.getsize(examples_path_es + 'atis.es'))
        os.remove(new_file)

    def test_write_es_dvs(self):
        parsed_file = loris.read_file(examples_path_es + 'dvs.es')
        new_file = 'new_dvs.es'
        loris.write_events_to_file(parsed_file, new_file)
        self.assertEqual(os.path.getsize(new_file), os.path.getsize(examples_path_es + 'dvs.es'))
        os.remove(new_file)

    def test_write_dvs_from_event_array_txyp(self):
        new_file = 'new_dvs.es'
        loris.write_events_to_file(self.event_array_txyp, new_file, self.ordering_txyp)
        parsed_file = loris.read_file(new_file)
        self.assertEqual(len(parsed_file['events']), 10000)

    def test_write_dvs_from_event_array_txyp_without_ordering(self):
        new_file = 'new_dvs.es'
        loris.write_events_to_file(self.event_array_txyp, new_file)
        parsed_file = loris.read_file(new_file)
        self.assertEqual(len(parsed_file['events']), 10000)

    def test_write_dvs_from_event_array_xytp(self):
        new_file = 'new_dvs.es'
        loris.write_events_to_file(self.event_array_xytp, new_file, self.ordering_xytp)
        parsed_file = loris.read_file(new_file)
        self.assertEqual(len(parsed_file['events']), 10000)

    def test_write_es_color(self):
        parsed_file = loris.read_file(examples_path_es + 'color.es')
        new_file = 'new_color.es'
        loris.write_events_to_file(parsed_file, new_file)
        self.assertEqual(os.path.getsize(new_file), os.path.getsize(examples_path_es + 'color.es'))
        os.remove(new_file)

    def test_write_es_generic(self):
        parsed_file = loris.read_file(examples_path_es + 'generic.es')
        new_file = 'new_generic.es'
        loris.write_events_to_file(parsed_file, new_file)
        self.assertEqual(os.path.getsize(new_file), os.path.getsize(examples_path_es + 'generic.es'))
        os.remove(new_file)

    def test_read_dat_v2_dvs(self):
        parsed_file = loris.read_file(examples_path_dat + 'NCARS_obj_004397_td.dat')
        events = parsed_file['events']
        self.assertEqual(len(events), 4407)
        self.assertEqual(parsed_file['type'], 'dvs')
        
    def test_read_dat_without_td_in_filename(self):
        parsed_file = loris.read_file(examples_path_dat + 'user01_do_3.dat')
        events = parsed_file['events']
        self.assertEqual(len(events), 723759)
        self.assertEqual(parsed_file['type'], 'dvs')
