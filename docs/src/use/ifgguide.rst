Compute an interferometric stack
################################

**Any EZ-InSAR coregistration job can be completed with an EZ-InSAR interferometric-stack job. The step names depends on the InSAR processor used during the coregistration.** This job will be used to generate interferograms/stack for time-series analysis processor (i.e., StaMPS or MintPy).

First, it is required to initiate the interferometric-stack job: 

.. code-block:: python
    
    job.initiateifg(modestack='normal')

The *modestack* value can be:
    - 'normal' to create a generic InSAR stack;  
    - 'stamps-ps' to create a PS stack for StaMPS; 
    - 'stamps-sbas' to create a SBAS stack for StaMPS; 
    - 'stamps-pssbas' to create a merged stack for StaMPS; 
    - 'mintpy' to create a stack for MintPy. 

The verbose option is available for each function. Of course, it is possible to check the interferometric-stack parameters (see the API documentation for further information such as the default parameters): 

.. code-block:: python

    job.ifgstack.check(verbose=True)

The user can modify any parameters: e.g.,: 

.. code-block:: python

    job.ifgstack.<step>[<parameter>]['value'] = <value of the parameter>

**To run a ifgstack step:**

.. code-block:: python

    job.ifgstack.run(step=<list of steps>)
    
If the step name *all* is used, **EZ-InSAR** will run all steps. 

With ISCE2 processor 
********************

For Sentinel-1 IW
=================

.. code-block:: python

    job.ifgstack.run(step=['ifgnetwork',
        'generate_burst_igram',
        'merge_burst_igram',
        'filter_coherence',
        'unwrap',
        'ifggeocoding',
        'finalstack'])

For StripMap-like data
======================

.. code-block:: python

    job.ifgstack.run(step=['ifgnetwork',
        'generate_igram',
        'filter_coherence',
        'unwrap',
        'ifggeocoding',
        'finalstack'])

With Doris processor 
********************

For StripMap-like data
======================

.. code-block:: python

    job.ifgstack.run(step=['importrslc',
        'refinerefdate',
        'ifgnetwork',
        'ifgcompute',
        'ifgfilter',
        'ifgunwrapping',
        'ifggeocoding',
        'finalstack'])

With SNAP processor 
********************

.. code-block:: python

    job.ifgstack.run(step=['ifgnetwork',
        'ifgcompute',
        'ifgnetwork',
        'ifgcompute',
        'ifgfilter',
        'multilook',
        'ifgunwrapping',
        'ifggeocoding',
        'finalstack'])

.. note:: 

    At the opposite of SNAP, **EZ-InSAR** has been developed with the ability of interferometric-stack updating. If a new is detected, only the InSAR products computed with this new images will be processed. The software behaviour is controlled by the forcing-mode super parameter:

    * if True: **EZ-InSAR** will reprocessed all images;
    * if False: **EZ-InSAR** will update images.

    This parameter can be modified by: 

    .. code:: python

        job.ifgstack.modeforcing = False 

    In addition, some SAR/InSAR processor can update the reference date of the stack (see the associated processor step). However, we want to notice that the consistency of data can be modified, and recommend avoiding this functionality. 
