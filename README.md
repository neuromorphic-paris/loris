# loris
read and write different file formats from neuromorphic cameras such as [.aedat](https://inivation.com/support/software/fileformat/), **.dat**, [.es](https://github.com/neuromorphic-paris/event_stream) or **.csv** and also [amazing animal](https://giphy.com/search/slow-loris)

### Supported formats
|        | version | read    | write   |
|--------|--------:|:-------:|:-------:|
| .aedat | 3.x     | &#9744; | &#9744; |
| .dat   | n/a     | &#9745; | &#9744; |
| .es    | 2.x     | &#9745; | &#9745; |
| .csv   | -       | &#9745; | &#9744; |

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

##### Loop over all events
~~~python
for event in events:
    print("ts:", event['ts'], "x:", event['x'], "y:", event['y'])
~~~

##### Write events to file using one of the three formats
~~~python
loris.write_events_to_file(events, "path_to_new_file")
~~~

Please use Pylint before creating a Pull Request. This will make loris happy

![loris](loris.gif "The Loris Banner")
