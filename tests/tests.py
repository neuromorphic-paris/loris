import loris
import os

examples_path = 'third_party/command_line_tools/third_party/sepia/third_party/event_stream/examples/'

def test_read_es_atis():
    file_atis = loris.read_file(examples_path + 'atis.es')
    assert 1326017 == len(file_atis['events'])
    assert 'atis' == file_atis['type']

def test_read_es_color():
    file_color = loris.read_file(examples_path + 'color.es')
    assert 473225 == len(file_color['events'])
    assert 'color' == file_color['type']

def test_read_es_dvs():
    file_dvs = loris.read_file(examples_path + 'dvs.es')
    assert 473225 == len(file_dvs['events'])
    assert 'dvs' == file_dvs['type']

def test_read_es_generic():
    file_generic = loris.read_file(examples_path + 'generic.es')
    assert 70 == len(file_generic['events'])
    assert 'generic' == file_generic['type']

def test_write_es_atis():
    file_atis = loris.read_file(examples_path + 'atis.es')
    new_file = 'new_atis.es'
    loris.write_events_to_file(file_atis, new_file)
    assert os.path.getsize(new_file) == os.path.getsize(examples_path + 'atis.es')
    os.remove(new_file)

def test_write_es_dvs():
    parsed_file = loris.read_file(examples_path + 'dvs.es')
    new_file = 'new_dvs.es'
    loris.write_events_to_file(parsed_file, new_file)
    assert os.path.getsize(new_file) == os.path.getsize(examples_path + 'dvs.es')
    os.remove(new_file)

def test_write_es_color():
    parsed_file = loris.read_file(examples_path + 'color.es')
    new_file = 'new_color.es'
    loris.write_events_to_file(parsed_file, new_file)
    assert os.path.getsize(new_file) == os.path.getsize(examples_path + 'color.es')
    os.remove(new_file)

def test_write_es_generic():
    parsed_file = loris.read_file(examples_path + 'generic.es')
    new_file = 'new_generic.es'
    loris.write_events_to_file(parsed_file, new_file)
    assert os.path.getsize(new_file) == os.path.getsize(examples_path + 'generic.es')
    os.remove(new_file)
