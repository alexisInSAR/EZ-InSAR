"""
Package for the Doris processor wrapper for **EZ-InSAR**

The package contains the different sub-modules to run `ezinsar` with Doris processor.

Changelog:
        * 1.2.1: Modification of the S1 reader, Oct. 2025, Alexis Hrysiewicz
        * 1.2.0: S1 orbit harmonisation (checking), Aug. 2025, Alexis Hrysiewicz
        * 1.1.0: Start the new supports (CSK, RSAT-2, TSX, PAZ), Feb. 2025, Alexis Hrysiewicz
        * 1.0.0: Initial version, Dec. 2024

"""

__namePackage__ = 'EZ-InSAR Doris Module'
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
# print('INFO: Load the EZ-InSAR Doris Module Version %s %s' % (__versionPackage__, __copyrightPackage__))