# loris
python3 library to handle different file formats from neuromorphic cameras such as **.dat**, [.aedat](https://inivation.com/support/software/fileformat/) or [.es](https://github.com/neuromorphic-paris/event_stream) and also [amazing animal](https://giphy.com/search/slow-loris)

### Install
~~~python
pip install loris
~~~

### How to loris
##### Read a file
~~~python
import loris
events = loris.read_file("path_to_file")
~~~
which returns a [numpy structured array](https://docs.scipy.org/doc/numpy/user/basics.rec.html) of event data.

##### Loop over all events
~~~python
for event in events:
    print("ts:", event['ts'], "x:", event['x'], "y:", event['y'])
~~~

##### Write events to file using one of the three formats
~~~python
loris.write_events_to_file(events, "path_to_new_file")
~~~


Please use Pylint before creating a Pull Request. [PEP 8 Python Style](https://www.python.org/dev/peps/pep-0008/) preferred. This will make loris happy

![loris](loris.gif "The Loris Banner")
