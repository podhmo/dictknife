as library (jsonknife)
========================================

- access by json pointer
- custom data loader

access by json pointer
----------------------------------------

access data by json pointer, you can use two functions, below.

- access_by_json_pointer
- assign_by_json_pointer

.. literalinclude:: ../../examples/library2/access_by_json_pointer00.py

result

.. literalinclude:: ../../examples/library2/access_by_json_pointer00.output

keyname within "/"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../examples/library2/access_by_json_pointer01.py

result

.. literalinclude:: ../../examples/library2/access_by_json_pointer01.output


custom data loader
----------------------------------------

Making your custom data loader, such as below.

- `$include` keyword for including extra files's contents

So, if you want to include extra data, you can do via `$include`.

.. code-block:: yaml

  main:
    subdata:
      $include <extra file path>

how to use it.

.. code-block:: bash

  $ python loader.py main.yaml > loader.output

input data are like below.

main.yaml

.. literalinclude:: ../../examples/library2/customloader/main.yaml

person.yaml

.. literalinclude:: ../../examples/library2/customloader/person.yaml

name.yaml

.. literalinclude:: ../../examples/library2/customloader/name.yaml

age.yaml

.. literalinclude:: ../../examples/library2/customloader/age.yaml

loaded data

.. literalinclude:: ../../examples/library2/customloader/loader.output
   :language: yaml

code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

loader.py

.. literalinclude:: ../../examples/library2/customloader/loader.py

another example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Resolver's constructor has `onload` argument, this is the hook called when loading data. you can make another version of custom data loader(almost same behavior), using this hook.

.. literalinclude:: ../../examples/library2/customloader/loader2.py
