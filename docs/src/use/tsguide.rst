Compute a time series of displacements
######################################

**An EZ-InSAR interferometric-stack job (or a coregistration job for GAMMA) can be completed with an EZ-InSAR time series analysis job.** The step names depends on the InSAR-TS processor. First, it is required to initiate the ts-processing job: 

.. code-block:: python
    
    job.initiatets(processor=<processor>)

Of course, it is possible to check the interferometric-stack parameters (see the API documentation for further information such as the default parameters): 

.. code-block:: python

    job.tsprocessing.check(verbose=True)

The user can modify any parameters: e.g.,: 

.. code-block:: python

    job.tsprocessing.<step>[<parameter>]['value'] = <value of the parameter>

**To run a tsprocessing step:**

.. code-block:: python

    job.tsprocessing.run(step=<list of steps>)
    
If the step name *all* is used, **EZ-InSAR** will run all steps. 

.. admonition:: Warning
  :class: Warning

    Do not forget to give the reference point. 

**EZ-InSAR tsprocessing job is prior to the configuration file of StaMPS and MintPy. If the user wants to read the built-in parameter files, it is required to use the following methods:**

    - *readparameters* for StaMPS;

    - *readcfg* for MintPy.

With MintPy processor
*********************

.. code-block:: python

    job.initiatets(processor='mintpy')
    job.tsprocessing.readcfg(job.tsprocessing, file = 'MintPy.cfg')
    job.tsprocessing.run(step=['load_data',
        'modify_network',
        'reference_point',
        'quick_overview',
        'correct_unwrap_error',
        'invert_network',
        'correct_LOD',
        'correct_SET',
        'correct_troposphere',
        'deramp',
        'correct_topography',
        'residual_RMS',
        'reference_date',
        'velocity',
        'geocode',
        'google_earth',
        'hdfeos5',
        'extract_res'])

With StaMPS processor
*********************

**For the PS or SBAS processing**:

.. code-block:: python

    job.initiatets(processor='stamps-ps') # or job.initiatets(processor='stamps-sbas')
    job.tsprocessing.run(step=['mt_prep',
        'load_data',
        'phase_noise',
        'ps_selection',
        'ps_weeding',
        'phase_correction',
        'phase_unwrapping',
        'corr_lkerror',
        'corr_noise',
        'extract_res'])

**For the merged processing** (the PS and SBAS processing should be made):

.. code-block:: python

    job.initiatets(processor='stamps-merged')
    job.tsprocessing.run(step=['merging',
        'phase_unwrapping',
        'corr_lkerror',
        'corr_noise',
        'extract_res'])

With LiCSBAS processor
**********************

.. admonition:: Warning
  :class: Warning

  No interferometric-stack processing is required.

.. code-block:: python

    job.initiatets(processor='licsbas')
    job.tsprocessing.detectframe()
    job.tsprocessing.run(step=['get_geotiff',
        'prep_ifg',
        'check_unw',
        'loop_closure',
        'sb_inv',
        'vel_std',
        'mask_ts',
        'filt_ts',
        'extract_res'])

.. note::

    After a time-series-analysis job, **EZ-InSAR-GUI** can be used for result visualisation. 



    