Compute a backscatter-intensity stack
#####################################

An **EZ-InSAR** job can be completed with an **EZ-InSAR** intensity-stack job. 

Firstly, it is required to initiate the intensity-stack job: 

.. code-block:: python
    
    job.initiateint(processor=<processor>)

.. note:: 

    The verbose option is available for each function. 

Of course, it is possible to check the intensity-stack parameters (see the API documentation for further information such as the default parameters): 

.. code-block:: python

    job.intstack.check(verbose=True)

The user can modify any parameters: e.g.,: 

.. code-block:: python

    job.intstack.<step>[<parameter>]['value'] = <value of the parameter>

**To run an intstack step:**

.. code-block:: python

    job.intstack.run(step=<list of steps>)
    
If the step name *all* is used, **EZ-InSAR** will run all steps. 

With SNAP processor
*******************

With SNAP, no coregistration will be done. Indeed, the intensity stack will be based on the Sentinel-1 image files. 

.. code-block:: python

    job.initiateint(processor='snap')
    job.intstack.run(step=['checkSLC','importSLC','multilook','filter','terraincal','geocode','clean','update'])