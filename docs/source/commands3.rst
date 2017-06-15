as command (swaggerknife)
========================================

- json2swagger
- flatten

json2swagger
----------------------------------------

input data

.. literalinclude:: ../../examples/deref/dst/data.yaml

.. code-block:: bash

  $ swaggerknife --name person json2swagger data.yaml > data2swagger.yaml

data2swagger.yaml

.. literalinclude:: ../../examples/deref/dst/data2swagger.yaml


flatten
----------------------------------------

only swagger like structure (toplevel is `#/definitions`).

.. code-block:: bash

  $ tree src
  src/
  └── abc.yaml

  $ mkdir -p dst
  $ jsonknife flatten --src src/abc.yaml --dst dst/abc.yaml

src/abc.yaml

.. literalinclude:: ../../examples/flatten/src/abc.yaml
   :language: yaml

dst/abc.yaml

.. literalinclude:: ../../examples/flatten/dst/abc.yaml
   :language: yaml
