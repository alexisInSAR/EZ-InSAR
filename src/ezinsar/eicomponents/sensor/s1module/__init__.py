"""
Module for the Sentinel-1 files in .zip and .SAFE format

The module allows to manage Sentinel-1 files in .zip and .SAFE format
    
    (From `ezinsar` package)

Changelog:
        1.2.1: Bug fix, Oct. 2025, Alexis Hrysiewicz
        1.2.0: Various changes, Aug. 2025, Alexis Hrysiewicz
            * S1 orbit harmonisation (and implementation of MOEORB)
            * ETAD downloading
        1.1.0: Various changes, Feb. 2025, Alexis Hrysiewicz
            * Start the migration of scripts into the APIs
            * Start the implementation of Sentinel-1 C and D
            * Some optimisations
        * 1.0.0: Initial version, Dec. 2024

"""

__namePackage__ = 'EZ-InSAR Sentinel-1 Module'
"""str: Name of the Python package.
"""

__authorPackage__ = 'Alexis Hrysiewicz (UCD / iCRAG)'
"""str: Name and afflilation of the main author
"""

__copyrightPackage__ =  "Copyright 2025, EZ-InSAR / UCD / iCRAG"
"""str: Copyright of the Python package
"""

__versionPackage__ = '1.2.1 Oct. 2025'
"""str: Current version of the Python package
"""

## Message 
# print('INFO: Load the EZ-InSAR Sentinel-1 Module Version %s %s' % (__versionPackage__, __copyrightPackage__))