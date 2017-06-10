as library (dictknife)
========================================

- pp
- deepmerge
- deepequal
- loading
- diff
- walkers
- accessor

pp
----------------------------------------

.. literalinclude:: ../../examples/library/pp00.py

result

.. literalinclude:: ../../examples/library/pp00.output


with OrderedDict
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../examples/library/pp01.py

result

.. literalinclude:: ../../examples/library/pp01.output

deepmerge
----------------------------------------

.. literalinclude:: ../../examples/library/deepmerge00.py

result

.. literalinclude:: ../../examples/library/deepmerge00.output

with override=True
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

..
   (in sphinx>1.6 using diff option with dictknife._sphinx patch)
.. literalinclude:: ../../examples/library/deepmerge01.py

result

.. literalinclude:: ../../examples/library/deepmerge01.output


deepequal
----------------------------------------

.. literalinclude:: ../../examples/library/deepequal00.py

result

.. literalinclude:: ../../examples/library/deepequal00.output


with normalize option
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../examples/library/deepequal01.py

result

.. literalinclude:: ../../examples/library/deepequal01.output

.. literalinclude:: ../../examples/library/deepequal02.py

result

.. literalinclude:: ../../examples/library/deepequal02.output


loading
----------------------------------------

support format

- yaml
- json
- toml

.. code-block:: python

   from dictknife import loading

   loading.setup()

   # load
   d = loading.loadfile("foo.yaml")
   d = loading.loadfile(None, format="yaml")  # from sys.stdin

   # dump
   loading.dumpfile(d, "foo.json")
   loading.dumpfile(d, None, format="toml")  # to sys.stdout

walkers
----------------------------------------

.. literalinclude:: ../../examples/library/walkers00.py

result

.. literalinclude:: ../../examples/library/walkers00.output

.. note::

   todo: description about chains and operator and context,...

