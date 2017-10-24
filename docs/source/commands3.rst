as command (swaggerknife)
========================================

- json2swagger
- flatten
- bundle

json2swagger
----------------------------------------

Generating swagger spec from data.

input data

.. literalinclude:: ../../examples/json2swagger/src/00config.json

.. code-block:: bash

  $ swaggerknife json2swagger config.json --name config --dst config-spec.yaml

config-spec.yaml

.. literalinclude:: ../../examples/json2swagger/dst/00config-spec.yaml
   :language: yaml

with multiple sources
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

with multiple sources, required option detection is more accrurately.

input data

person-foo.json

.. literalinclude:: ../../examples/json2swagger/src/01person-foo.json

person-bar.json

.. literalinclude:: ../../examples/json2swagger/src/01person-bar.json

.. code-block:: bash

  $ swaggerknife json2swagger person-foo.json person-bar.json --name person --dst person-spec.yaml

person-spec.yaml

.. literalinclude:: ../../examples/json2swagger/dst/01person-spec.yaml
   :language: yaml

01person-bar.json doesn't have nickname and nickname is not reuired in generated spec.


with `---annotate` option
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

with annotation file.


with-annotations.yaml

.. literalinclude:: ../../examples/json2swagger/src/02with-annotations.yaml
   :language: yaml

annotations.yaml

.. literalinclude:: ../../examples/json2swagger/src/02annotations.yaml
   :language: yaml

.. code-block:: bash

   swaggerknife json2swagger with-annotations.yaml --annotate=annotations.yaml --name Top --dst with-annotations-spec.yaml

with-annotations-spec.yaml

.. literalinclude:: ../../examples/json2swagger/dst/02with-annotations-spec.yaml
   :language: yaml

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

bundle
----------------------------------------

.. code-block:: bash

  $ tree src
  src/
  ├── api
  │   ├── me.json
  │   └── user.json
  ├── definitions
  │   ├── primitive.json
  │   └── user.json
  └── main.json


src/main.json

.. literalinclude:: ../../examples/linker/src/main.json

src/api/me.json

.. literalinclude:: ../../examples/linker/src/api/me.json

src/api/user.json

.. literalinclude:: ../../examples/linker/src/api/user.json

src/definitions/primitive.json

.. literalinclude:: ../../examples/linker/src/definitions/primitive.json

src/definitions/user.json

.. literalinclude:: ../../examples/linker/src/definitions/user.json

bundle output
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

bundle output is this.

.. code-block:: bash

   $ swaggerknife bundle --src src/main.json --dst bundle.yaml

   # if you want json output
   $ swaggerknife bundle --src src/main.json --dst bundle.json

bundle.yaml

.. literalinclude:: ../../examples/linker/bundle.yaml
   :language: yaml
