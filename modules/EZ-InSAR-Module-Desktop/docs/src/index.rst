EZ-InSAR Desktop Module
#######################

Welcome to the documentation of **EZ-InSAR Desktop Module**

.. admonition:: EZ-InSAR
  :class: warning

  **EZ-InSAR Desktop Module** is still under development and tests. 

**EZ-InSAR Desktop Module** is a supplementary module for **EZ-InSAR** in order to add a friendly Graphical User Interface to **EZ-InSAR**. **EZ-InSAR** therefore is required to run this Python package. 

Use of EZ-InSAR Desktop Module
------------------------------

After installing the module, you can use **EZ-InSAR** with the Graphical User Interface.

The documentation of **EZ-InSAR Desktop Module** can be launched with this command: 

.. code-block:: bash
  
  ezinsar docs -m desktop

Installation of EZ-InSAR Desktop Module
---------------------------------------

The installation of this module can be perfomed as a normal Python package. There is not requirements because they were installed by the core of **EZ-InSAR**.

.. code-block:: bash
  
  pip3 install -e .

Run EZ-InSAR with the Graphical User Interface
----------------------------------------------

.. code-block:: bash
  
  ezinsar

or, for a specific GUI tools

.. code-block:: bash
  
  ezinsar desktop <tool name> <options/arguments>

.. toctree::
  :maxdepth: 1
  :caption: Documentation

  mainwindow/mainwindow
  applications/index
  settings/settings
  tools/index
  authors
  changelog
  acknowledgments
  licenses

.. toctree::
   :maxdepth: 1
   :caption: Quick links

   api/index
   EZ-InSAR's GitHub <https://github.com/alexisInSAR/EZ-InSAR-Module-Desktop>
   University College Dublin <https://www.ucd.ie>
   iCRAG <https://www.icrag-centre.org>
