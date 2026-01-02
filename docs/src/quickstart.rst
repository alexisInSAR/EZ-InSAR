Quick Start
###########

Spirit of EZ-InSAR
******************

**EZ-InSAR** manipulates **EZ-InSAR** job classes. This class contains the full set of parameters - required for SAR/InSAR computations - (e.g., satellite name, multilook factors, etc.) and several processing jobs (or sub-jobs, e.g.,):

* a processing job for coregistration; 
* a processing job for interferometric computation; 
* a processing job for time-series analysis.

**EZ-InSAR** jobs can be easily imported and exported to .xml-format file allowing any user changes. The SAR/InSAR processor is transparent for users. 

Run EZ-InSAR
************

First, we recommend reading the **EZ-InSAR**'s documentation. If available, **EZ-InSAR** will display an online version of documentation. If not, **EZ-InSAR** will display an offline version. Some differences may be visible regarding the user's version of **EZ-InSAR**. Please, use the following command to launch the documentation, in your favorite terminal. 

.. code-block:: bash

    ezinsar docs

The documentation of scripts is available and *help* function can be used in Python environment. 

Then, **EZ-InSAR can be launched via three different ways:**

1. by command-line interface: the easiest way to use **EZ-InSAR**; 
2. within a Python environment: most powerfull way to use **EZ-InSAR**; 
3. by using the Graphic-User-Interface (GUI) of **EZ-InSAR**.

.. note::

    **Our recommendations, as a function of user's level, are as follows:** 

    1. for the *beginners*: GUI; 
    2. for the *intermediate users*: command-line interface of **EZ-InSAR**; 
    3. fot the *experts*: Python scripts should be the most versatible option and command-line interface. 

.. tabs::

    .. tab:: Command-line interface

        **EZ-InSAR** can be used with command-line interface. An useful start would be to display the different options/commands of **EZ-InSAR**:

        .. code-block:: bash

            ezinsar -h 

        If the command is correct, the help - associated to the command - can be displayed:

        .. code-block:: bash

            ezinsar <command> -h 

        before to launch any **EZ-InSAR** command:

        .. code-block:: bash

            ezinsar <command> <argument> [options]

    .. tab:: In Python

        **EZ-InSAR** can be used directly in Python, via a Python script for example. It is the most powerful approach. Numerous options are available, so we recommend checking the documentation: 
        
        Firslty, **EZ-InSAR** must be imported:

        .. code-block:: python

            import ezinsar.job as ez

        Then, the **EZ-InSAR** can be initialised: 

        .. code-block:: python
            
            job = ez.EIjob()

    .. tab:: With the Graphical User Interface

        **EZ-InSAR GUI** can be launched by (optional module is required): 

        .. code-block:: bash

            ezinsar 

**By our experience, the EZ-InSAR's authors noticed that the natural usage of EZ-InSAR is**

1. Creation of **EZ-InSAR** job (and modification of some parameters) using Python; 
2. Use of command-line interface for computation and processing; 
3. Use of graphical-user interface for rapid visualisation of results. 

The *examples page* contains several examples in order to understand the use of **EZ-InSAR**.