Installation of SAR/InSAR processors
====================================

.. admonition:: Warning
    :class: warning

    The *installation* page is not completed and we are actively working on this page in order to provide accurate guidelines for SAR/InSAR-processor installations. 

    **We recommend using the installation instructions of EZ-InSAR-2 to install ISCE-2, StaMPS and MintPy.** The .pdf document can be found in GitHub. 


**Each SAR and InSAR processor needs to be installed by user.**

.. admonition:: Warning
    :class: warning

    After installation of a processor, please update your EZ-InSAR configuration file: 

    .. code-block:: bash

        ezinsar toolkit configfile

For ISCE-2
^^^^^^^^^^

ISCE-2 is installed by *conda*: 

.. code-block:: bash

    conda install -c conda-forge isce2

However, **EZ-InSAR** will use the *contrib* scripts. The user should clone the GitHub repository. 

.. code-block:: bash

    git clone https://github.com/isce-framework/isce2.git 

We recommend installing ISCE-2 after **EZ-InSAR** in order to keep the same conda environment.

For SNAP
^^^^^^^^

SNAP should be installed and "linked" to your Python environment (see https://step.esa.int/main/download/snap-download/).

The version 11 is required following the correction of critical bugs, however the installation of snappy is not automatic. Please see https://senbox.atlassian.net/wiki/spaces/SNAP/pages/2499051521/Configure+Python+to+use+the+new+SNAP-Python+esa_snappy+interface+SNAP+version+10 to order to install the Python wrapper. 

**We recommend using GPT with EZ-InSAR-3, however some parts of coregistration processing can be carried out with snappy.**

For Doris
^^^^^^^^^

The most recent version of Doris can be clone by using git: 

.. code-block:: bash

    git clone https://github.com/TUDelftGeodesy/Doris.git 

The Doris' authors provides guidelines for its installation. 

.. note:: 

    gcc and g++ in version lower than 5 are required for Doris. 

**It is mandatory to install Doris AND StaMPS.**

For MintPy
^^^^^^^^^^

.. code-block:: bash

    pip3 install mintpy

For StaMPS
^^^^^^^^^^

The most recent version of StaMPS can be clone by using git: 

.. code-block:: bash

    git clone https://github.com/dbekaert/StaMPS.git

The StaMPS' authors provides guidelines for its installation. 

.. note:: 

    **However, please find some important notes about the StaMPS' installation:**

        - Users need to have their MATLAB version installed, and the *matlab.engine* ready under Python. 

        - The installation of Doris requires the installation of StaMPS.

        - **EZ-InSAR** will not install the *matlab.engine* Python package to avoid creating any conflicts between MATLAB and Python. Please install it. 

For LiCSBAS
^^^^^^^^^^^

EZ-InSAR requires several LiCSAR and LiCSBAS Python packages. We clone the GitHub repositories in the same directories (i.e., LiCSBAS_packages): 

.. code-block:: bash

    git clone https://github.com/comet-licsar/LiCSBAS.git
    git clone https://github.com/comet-licsar/licsar_proc.git
    git clone https://github.com/comet-licsar/licsar_extra.git

Then, users can install the package using pip manager:

.. code-block:: bash 

    cd LiCSBAS 
    pip3 install -e . 

    cd licsar_proc 
    pip3 install -e . 

    cd licsar_extra 
    pip3 install -e .
