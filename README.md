# loris
python3 library to handle event-based file formats such as [.es](https://github.com/neuromorphic-paris/event_stream), [.dat]() or [.aedat](https://inivation.com/support/software/fileformat/) and also [amazing animal](https://giphy.com/search/slow-loris)

### Install
~~~python
pip install loris
~~~

#### Dependencies
 - numpy

### How to loris
To read a file, use

~~~python
import loris
stream = loris.readsteam("filename")
~~~

The function returns a [numpy recarray](https://docs.scipy.org/doc/numpy/reference/generated/numpy.recarray.html) containing an array of event data
Each field can be accessed using its name as ``stream.data.<fieldname>`` which returns again an array.

As an example to loop over all events:
~~~python
for datum in stream data:
    print (data.ts)
~~~

Please use Pylint before creating a Pull Request. [PEP 8 Python Style](https://www.python.org/dev/peps/pep-0008/) preferred. This will make loris happy

![loris](loris.gif "The Loris Banner")
