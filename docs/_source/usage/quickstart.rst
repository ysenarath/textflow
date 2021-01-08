Quick Start
===========

Creating a Project
------------------

Project can be created using following command:

.. code-block::

   textflow project create -t "<project type>" -n "<project name>"

List Projects
------------------

To see all available projects we can use:

.. code-block::

   textflow project list

Creating Labels
---------------

.. code-block::

   textflow label create -p <Project ID> -l "<Label>" -v "<Value>"

Upload Documents
----------------

.. code-block::

   textflow document upload -p <Project ID> -i "<Input File Path>"

Creating a User
---------------

.. code-block::

   textflow user create -u <User Name> -p <Password>

Assign User to Project
----------------------

.. code-block::

   textflow user assign -u "<User Name>" -p <Project ID>

Serve the Project
-----------------

Once all project information is added in the project you can start server by creating a script:


.. code-block::

   import json
   import os

   from textflow import TextFlow

   with open(os.path.join(os.getcwd(), 'config.json')) as fp:
      config = json.load(fp)

   tf = TextFlow(config)

   if __name__ == '__main__':
      tf.app.run(debug=True)

Here, `config.json` is automatically created when first project is initialized.