# Loris
[![Travis](https://img.shields.io/travis/neuromorphic-paris/loris/master.svg?label=Travis%20CI)](https://www.travis-ci.org/neuromorphic-paris/loris)

read and write different file formats from neuromorphic cameras such as **.dat**, [.es](https://github.com/neuromorphic-paris/event_stream) or **.csv** and also [amazing animal](https://giphy.com/search/slow-loris)

If you're planning to read **.aedat** files, take a look at [dv-python](https://gitlab.com/inivation/dv-python)

### Supported formats
|        | version | read    | write   |
|--------|--------:|:-------:|:-------:|
| .dat   | 1/2     | &#9745; | &#9744; |
| .es    | 2.x     | &#9745; | &#9745; |
| .csv   | -       | &#9745; | &#9744; |

### Install
~~~python
pip install loris
~~~

### How to loris
##### Read a file, for example a .dat file and loop over all events
~~~python
import loris
my_file = loris.read_file("/path/to/my-file.dat")
events = my_file['events']

for event in events:
    print("ts:", event.t, "x:", event.x, "y:", event.y, "p:", event.p)
~~~

##### Write events from an array to an .es file
~~~python
ordering = "xytp"  # corresponds to the order in your array
loris.write_events_to_file(event_array, "/path/to/my-file.es", ordering)
~~~

##### Write structured events (with dtypes) to an .es file
~~~python
loris.write_events_to_file(structured_event_array, "/path/to/my-file.es")
~~~


![loris](loris.gif "The Loris Banner")
