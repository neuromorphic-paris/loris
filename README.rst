loris
=====

python3 library to handle event-based file formats such as
`.es <https://github.com/neuromorphic-paris/event_stream>`__,
.dat or
`.aedat <https://inivation.com/support/software/fileformat/>`__ and also
`amazing animal <https://giphy.com/search/slow-loris>`__

Install
~~~~~~~

Currently only locally. Soon to be released via PyPi. Dependencies
- numpy

How to loris
~~~~~~~~~~~~

To read a file, use

.. code:: python

    import loris
    stream = loris.readsteam("filename")

The function returns a `numpy
recarray <https://docs.scipy.org/doc/numpy/reference/generated/numpy.recarray.html>`__
containing an array of event data Each field can be accessed using its
name as ``stream.data.<fieldname>`` which returns again an array.

As an example to loop over all events:

.. code:: python

    for datum in stream data:
    print (datum.ts)

Please use Pylint before creating a Pull Request. `PEP 8 Python
Style <https://www.python.org/dev/peps/pep-0008/>`__ preferred. This
will make loris happy

.. figure:: loris.gif
   :alt: The Loris Banner
