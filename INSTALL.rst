Installation
============

.. admonition:: Experimental
    :class: warning

    Binary installers will be available `here <https://github.com/alexisInSAR/EZ-InSAR/tree/main/installer>`_ They can be used after installations of the requirements.

    However, we recommend using the sources because installers are experimental.

    After downloading EZ-InSAR from Github:

    .. code:: bash

        cd EZ-InSAR/installer
        pip3 install pyqt5
        pip3 install requests
        python3 ./EZInSAR_Installer.py

    **Use the parent directory of the EZ-InSAR as an installation directory. At contrary, the installer will download the packages.**

Requirements
------------

**First, EZ-InSAR needs several requirements.**

Python 3
^^^^^^^^

The version of Python requires to be >= 3.8 and <=3.11. We recommend using 3.10.XX. miniconda3 also needs to be installed and ready for **EZ-InSAR**. all information can be found `here <https://www.anaconda.com/docs/getting-started/miniconda/install>`_. Of course, manual installation can be performed. 

GDAL
^^^^

**EZ-InSAR** uses GDAL for various purproses: binary and Python binding. All information can be found `here <https://gdal.org/en/stable/>`_. There is not required version but versions >3.8 should be preferred. 

.. admonition:: Difficulty
    :class: warning

    It can be very difficult to install GDAL. Please take care that the Python API and the GDAL library have the same version. conda can be used to easily install all the packages.

Amazon Command Line Interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

aws-cli program is use by **EZ-InSAR** for Digital Elevation Model donwloading. All information can be found `here <https://aws.amazon.com/cli/>`_.

git
^^^

git tool can be required by **EZ-InSAR** to manage the different modules and updates. In this case, the .my-credential or .git-credential files are required. The .my-credential or .git-credential files can be created by: 

.. code:: bash

    git config credential.helper store
    + any git push or pull 
  
Docker
^^^^^^

For Windows, Docker is mandatory such as the EZ-InSAR image. 

Installation of EZ-InSAR
------------------------

.. admonition:: Installation directory
    :class: note

    We recommend having this directory structure:

    - <Installation directory>
        
        -> EZ-InSAR
        
        -> EZ-InSAR-Module-<Name of the module 1>
        
        -> EZ-InSAR-Module-<Name of the module 2>
        
        -> EZ-InSAR-Module-<Name of the module 3>
        
        -> ...

The Python-based packages required by **EZ-InSAR** are given with the *requirements* file. **The users should be aware that the GDAL python and GDAL library must be compatible regarding their versions.** **It is recommended to create** a *conda* environment for **EZ-InSAR**:

.. code-block:: bash

    conda create --name EZ-InSAR-3 python=3.10
    conda install -c conda-forge h5py
    conda install -c conda-forge libgdal==3.10 # Can be required for Windows
    conda install -c conda-forge gdal==3.10

However, several 3rd-party software can be required for each SAR/InSAR processors: i.e., snaphu and triangle software are required for most of InSAR processor. For example, their installations can be done with (for Linux systems): 
    
.. code-block:: bash
        
    sudo apt-get install snaphu
    sudo apt-get install triangle-bin

.. note:: 

    The Docker file can be used to identify the required installations for Ubuntu Linux-based system.

**pip manager is used for EZ-InSAR installation:**

.. code-block:: bash

    cd <path of EZ-InSAR>

.. code-block:: bash

    pip3 install -r requirements.txt # for the required packages
    pip3 install -r requirementsdocs.txt # for the required packages for docs compilation (optional)
    pip3 install -e . # install EZ-InSAR

.. note:: 

    **We strongly recommend installing EZ-InSAR with "-e ." because of the editable mode of pip3 manager. This will unlock some features of EZ-InSAR and allow a better bug tracking.**

**In order to configure EZ-InSAR, users can use to the following command**

.. code:: bash

    ezinsar toolkit configfile
    ezinsar toolkit shortcut # Create the desktop shortcuts of EZ-InSAR

Installation of EZ-InSAR modules
--------------------------------

If EZ-InSAR is downloaded from the public release, some optional modules of EZ-InSAR are offered. Please move the module directories into your EZ-InSAR toolkit directory: 

.. code-block:: bash
    
    cd EZ-InSAR/modules 
    mv EZ-InSAR-Module-* ../../

**EZ-InSAR** modules can be installed using *pip3*: 

.. code-block:: bash

    cd EZ-InSAR-Module-<Name of the EZ-InSAR module>
    pip3 install -e . 

Supplementary for the experts
-----------------------------

Users can modify the variables in the *constants.py* file of **EZ-InSAR**. Be carefull, these parameters can change the beahviour of **EZ-InSAR**. 
 
Installation with Docker
------------------------

For the non-Linux system, **EZ-InSAR** is provided with a Docker Makefile, which can be used to create a Docker Container in order to run **EZ-InSAR** on other operating system. However, only the open-source - and no MATLAB-based - processor will be installed (**ISCE2 and MintPy**). **Please follow the installation steps:**

1. Installation of Docker in the local machine. We recommend installing the Docker Hub software.  
2. The option *Allow the default Docker socket to be used (requires password)* could be enabled (e.g., it was required for a MacOS installation). 
3. Go to the **EZ-InSAR** directory in order to build the Docker image. Here we ask Docker to install an AMD64 version of Linux. This option can be required for installation on MacOS Silicon-based system. 

    .. code-block:: bash 

        docker build --platform linux/amd64 -t ezinsar -f docker/dockerfile . 

4. The **EZ-InSAR** image is now ready. A container can be launched (by a Docker command OR by an **EZ-InSAR** command): 

    .. code-block:: bash 

        docker run --name ezinsar0 -p 8050:8050 -it ezinsar [+ any options]

    In addtion, **EZ-InSAR** has a command for running the Docker container. Users can easly mount the external work directory onto the Docker container. 

    .. code-block:: bash 

        ezinsar docker -v <pathofworkdirectory> 

.. note::

    EZ-InSAR Graphical User Interface is able to deal with the docker container but the image needs to be created and available. Please run the previous steps: 1, 2 and 3. 

Installation on Windows
-----------------------

From the version 3.2.0, EZ-InSAR offers the support of SAR/InSAR processing on Windows. For the installation:

1. install the EZ-InSAR toolkit, with the similar way of Linux users, but only the SNAP processor should be installed;
2. create the Docker image; 
3. The user needs to make sure that the PYTHONPATH is available (set PYTHONPATH="" in the Windows terminal)
4. **ALL the directories (ie., SLC, orbits, etc.) must be in the work directory, if Docker is used.**


