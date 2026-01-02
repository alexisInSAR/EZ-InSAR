"""
Module for the ISCE-2 processor wrapper for **EZ-InSAR**

The module contains the different sub-modules to run `ezinsar` with ISCE (version 2) processor.

Changelog:
        * 1.2.0: New checking of S1 orbit, Aug. 2025, Alexis Hrysiewicz
        * 1.1.0: Start the supports of CSK, RSAT-2, Feb. 2025, Alexis Hrysiewicz
        * 1.0.0: Initial version, Dec. 2024

"""

__namePackage__ = 'EZ-InSAR ISCE-2 Module'
"""str: Name of the Python package.
"""

__authorPackage__ = 'Alexis Hrysiewicz (UCD / iCRAG)'
"""str: Name and afflilation of the main author
"""

__copyrightPackage__ =  "Copyright 2025, EZ-InSAR / UCD / iCRAG"
"""str: Copyright of the Python package
"""

__versionPackage__ = '1.2.0 Feb. 2025'
"""str: Current version of the Python package
"""

## Message 
# print('INFO: Load the EZ-InSAR ISCE-2 Module Version %s %s' % (__versionPackage__, __copyrightPackage__))