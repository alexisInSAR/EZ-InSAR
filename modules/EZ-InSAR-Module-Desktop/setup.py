#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-
"""EZInSAR setuptools configuration"""

githublink='https://github.com/alexisInSAR/EZ-InSAR-Module-Desktop.git'

from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open("README.rst", "r") as readme_file:
    readme = readme_file.read()

setup(name='EZ-InSAR Desktop Module', 
    version='1.1.3', 
    author="Alexis Hrysiewicz UCD/iCRAG",
    author_email="alexis.hrysiewicz@ucd.ie",
    description="EZ-InSAR Desktop Module",
    long_description=readme,
    long_description_content_type="text/rst",
    url=githublink,
    project_urls={
        'Repository': githublink,
        'Documentation': 'https://alexisinsar.github.io/EZ-InSAR/',
        'Issue Tracker': 'https://github.com/alexisInSAR/EZ-InSAR-Module-Desktop/issues',
    },
    install_requires= required,
    packages=find_packages('ezinsardesktopmodule'),
    package_dir = {"": "src"},
        python_requires='>=3.8',
    license='GPL-v3',
    license_files=('LICENSE',),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GPL-v3",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development",
        "Topic :: Scientific/Engineering :: Earth Sciences",
    ],
    entry_points={
            'console_scripts': ['ezinsardesktop_create=ezinsardesktopmodule.job.jobcreationWizard:main',
                                'ezinsardesktop_parameter=ezinsardesktopmodule.job.jobparameterWidget:main',
                                'ezinsardesktop_directory=ezinsardesktopmodule.job.jobdirectoryWidget:main',
                                'ezinsardesktop_log=ezinsardesktopmodule.log.logWidget:main',
                                'ezinsardesktop_roi=ezinsardesktopmodule.roi.roiWidget:main',
                                'ezinsardesktop_satparameter=ezinsardesktopmodule.sat.satparameterWidget:main',
                                'ezinsardesktop_SLClist=ezinsardesktopmodule.sat.SLClistTableWidget:main',
                                'ezinsardesktop_SLCmap=ezinsardesktopmodule.sat.SLCMapWidget:main',
                                'ezinsardesktop_downloader=ezinsardesktopmodule.sat.SARDownloaderWidget:main',
                                'ezinsardesktop_DEM=ezinsardesktopmodule.dem.DEMWidget:main',
                                'ezinsardesktop_initprocess=ezinsardesktopmodule.process.processInitDialog:main',
                                'ezinsardesktop_parameterprocess=ezinsardesktopmodule.process.processParameterWidget:main',
                                'ezinsardesktop_run=ezinsardesktopmodule.process.processRunDialog:main',
                                'ezinsardesktop_config=ezinsardesktopmodule.config.configDial:main',
                                'ezinsardesktop_about=ezinsardesktopmodule.config.aboutDial:main',
                                'ezinsardesktop_license=ezinsardesktopmodule.config.licenseDial:main',
                                'ezinsardesktop_S1track=ezinsardesktopmodule.sat.tools.s1.S1detectionWidget:main',
                                'ezinsardesktop_S1baselines=ezinsardesktopmodule.sat.tools.s1.S1ASFbaselinesWidget:main',
                                'ezinsardesktop_epsg=ezinsardesktopmodule.tools.EPSGcodeDial:main',
                                'ezinsardesktop_imagedisplayer=ezinsardesktopmodule.display.imageWidget:main',
                                'ezinsardesktop_mapdisplayer=ezinsardesktopmodule.display.mapWidget:main',
                                'ezinsardesktop_exportdata=ezinsardesktopmodule.interface.exportEZdataWidget:main',
                                'ezinsardesktop_docs=ezinsardesktopmodule.tools.docsWidget:main',
                                ]},
    )