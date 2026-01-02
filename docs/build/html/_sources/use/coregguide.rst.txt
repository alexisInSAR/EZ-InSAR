Run a coregistration of SLCs 
############################

**An EZ-InSAR job can be concatenated with an EZ-InSAR coregistration job. The use is similar for all processors but the steps can be different.**

First, it is required to initiate the coregistration job: 

.. code-block:: python
    
    job.initiatecoreg(processor=<name of the processor>)

The verbose option is available for each function. 

Of course, it is possible to check the coregistration parameters (see the API documentation for further information such as the default parameters): 

.. code-block:: python

    job.coregistration.check(verbose=True)

Then, the user can modify any parameters: e.g.,: 

.. code-block:: python

    job.coregistration.<step>[<parameter>]['value'] = <value of the parameter>

**To run a coregistration step:**

.. code-block:: python

    job.coregistration.run(step=[<list of steps>])
    
If the step name *all* is used, **EZ-InSAR** will run all steps. 

With ISCE2 processor 
********************

With the ISCE2 processor, the coregistration job will be initiated with: 

.. code-block:: python
    
    job.initiatecoreg(processor='isce2')

Then, the coregistration steps can be launched. 

For Sentinel-1 IW
=================

.. code-block:: python

    job.coregistration.run(step=['checkSLC',
        'checkOrbit',
        'coarserefdate',
        'unpack_topo_reference',
        'average_baseline',
        'extract_burst_overlaps',
        'overlap_geo2rdr',
        'overlap_resample',
        'pairs_misreg',
        'timeseries_misreg',
        'fullBurst_geo2rdr',
        'fullBurst_resample',
        'extract_stack_valid_region',
        'merge_reference_secondary_slc',
        'grid_baseline'])

For StripMap-like data
======================

.. code-block:: python    

    job.coregistration.run(step=['checkSLC',
        'checkOrbit',
        'coarserefdate',
        'unpack_slc',
        'crop_slc',
        'reference',
        'focus_split',
        'geo2rdr_coarseResamp',
        'refineSecondaryTiming',
        'invertMisreg',
        'fineResamp',
        'grid_baseline'])

With Doris processor 
********************

With the Doris processor, the coregistration job will be initiated with: 

.. code-block:: python
    
    job.initiatecoreg(processor='doris')

Then, the coregistration steps can be launched. 

For StripMap-like data
======================

.. code-block:: python   

    job.coregistration.run(step=['checkSLC',
        'checkOrbit',
        'coarserefdate',
        'extractimage',
        'refinerefdate',
        'mastertiming',
        'oversample',
        'coarseoffset',
        'finecoreg',
        'reltiming',
        'demassist',
        'coregpm',
        'resample',
        'finalstack',
        'cleanstack'])

With SNAP processor 
********************

With the SNAP processor, the coregistration job will be initiated with: 

.. code-block:: python
    
    job.initiatecoreg(processor='snap')

Then, the coregistration steps can be launched. 

.. code-block:: python   

    job.coregistration.run(step=['checkSLC',
        'coarserefdate',
        'importSLC',
        'refinerefdate',
        'coreg',
        'cleanstack'])

.. note:: 

    The coregistration job with SNAP has not the ability to be updated from new acquisitions. 


    