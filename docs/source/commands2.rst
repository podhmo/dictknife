as command (jsonknife)
========================================

Handling JSON data espencially swagger like structure.

- cut
- deref
- examples

deref and cut
----------------------------------------

.. code-block:: bash

  $ tree src
  src
  └── colors.yaml

src/colors.yaml

.. literalinclude:: ../../examples/cut/src/colors.yaml
   :language: yaml

deref
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

deref is unwrap function.

.. code-block:: bash

  mkdir -p dst
  jsonknife deref --src src/colors.yaml --ref "#/rainbow/yellow" > dst/00dref.yaml
  jsonknife deref --src src/colors.yaml --ref "#/rainbow/yellow@yellow" > dst/01dref.yaml
  jsonknife deref --src src/colors.yaml --ref "#/rainbow/yellow@yellow" --ref "#/rainbow/indigo@indigo" > dst/02dref.yaml

dst/00deref.yaml with `--ref "#/rainbow/yellow"`

.. literalinclude:: ../../examples/cut/dst/00deref.yaml
   :language: yaml

dst/01deref.yaml with `--ref "#/rainbow/yellow@yellow"`

.. literalinclude:: ../../examples/cut/dst/01deref.yaml
   :language: yaml

dst/02deref.yaml with `--ref "#/rainbow/yellow@yellow" --ref "#/rainbow/indigo@indigo"`

.. literalinclude:: ../../examples/cut/dst/02deref.yaml
   :language: yaml

cut
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   $ jsonknife cut --src ./dst/02deref.yaml --ref "#/yellow" > ./dst/00cut.yaml

dst/00cut.yaml

.. literalinclude:: ../../examples/cut/dst/00cut.yaml
   :language: yaml


deref
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

deref output
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

deref output is this.

.. code-block:: bash

   $ jsonknife deref --src src/main.json --dst deref.yaml

   # if you want json output
   $ jsonknife deref --src src/main.json --dst deref.json

deref.yaml

.. literalinclude:: ../../examples/linker/deref.yaml
   :language: yaml


examples
----------------------------------------

.. code-block:: bash

   $ tree src
   src/
   ├── person.yaml
   └── primitive.yaml

   $ jsonknife deref --src src/person.yaml --dst dst/extracted.yaml --ref "#/definitions/person"
   $ jsonknife examples dst/extracted.yaml --format yaml > dst/data.yaml

src/person.yaml

.. literalinclude:: ../../examples/deref/src/person.yaml
   :language: yaml

src/primitive.yaml

.. literalinclude:: ../../examples/deref/src/primitive.yaml
   :language: yaml

dst/extracted.yaml

.. literalinclude:: ../../examples/deref/dst/extracted.yaml
   :language: yaml

dst/data.yaml

.. literalinclude:: ../../examples/deref/dst/data.yaml
   :language: yaml
