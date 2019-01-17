
![loris](loris.gif "The Loris Banner")
# loris
python3 library to handle [EventStream](https://github.com/neuromorphic-paris/event_stream) files

### Install
Currently only locally. Soon to be released via PyPi.
#### Dependencies
 - numpy

### Use
To read an .es file, use

~~~python
import loris
stream = loris.readsteam("filename")
~~~

The function returns a [numpy recarray](https://docs.scipy.org/doc/numpy/reference/generated/numpy.recarray.html) containing an array of event data, which can in turn be accessed by calling ``stream.data``
Each field can be accessed using its name as ``stream.data.<fieldname>`` which returns again an array.

As an example to loop over all events:
~~~python
for datum in stream data:
    print (data.ts)
~~~

Please use Pylint before creating a Pull Request. [PEP 8 Python Style](https://www.python.org/dev/peps/pep-0008/) preferred.

Caveat: writing a generic event stream is not implemented yet
