#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-
"""EZInSAR setuptools configuration"""

githublink='https://github.com/alexisInSAR/EZ-InSAR.git'

from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open("README.rst", "r") as readme_file:
    readme = readme_file.read()

setup(name='EZ-InSAR', 
    version='3.3.1', 
    author="Alexis Hrysiewicz UCD/iCRAG",
    author_email="alexis.hrysiewicz@ucd.ie",
    description="EZ-InSAR Toolbox",
    long_description=readme,
    long_description_content_type="text/rst",
    url=githublink,
    project_urls={
        'Repository': githublink,
        'Documentation': 'https://alexisinsar.github.io/EZ-InSAR/',
        'Issue Tracker': 'https://github.com/alexisInSAR/EZ-InSAR/issues',
    },
    packages=find_packages('ezinsar'),
    package_dir = {"": "src"},
        python_requires='>=3.8',
    install_requires= required,
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
        'console_scripts': ['ezinsar=ezinsar.cli.ezinsarapp:main',
                            'ezinsarapp_download=ezinsar.cli.ezinsarapp_download:main',
                            'ezinsarapp_S1orbit=ezinsar.cli.ezinsarapp_S1orbit:main',
                            'ezinsarapp_S1planned=ezinsar.cli.ezinsarapp_S1planned:main',
                            'ezinsarapp_S1etad=ezinsar.cli.ezinsarapp_S1etad:main',
                            'ezinsarapp_DEM=ezinsar.cli.ezinsarapp_DEM:main',
                            'ezinsarapp_init=ezinsar.cli.ezinsarapp_init:main',
                            'ezinsarapp_run=ezinsar.cli.ezinsarapp_run:main',
                            'ezinsarapp_bestref=ezinsar.cli.ezinsarapp_bestref:main',
                            'ezinsarapp_lastS1=ezinsar.cli.ezinsarapp_lastS1:main',
                            'ezinsarapp_quickifg=ezinsar.cli.ezinsarapp_quickifg:main',
                            'ezinsarapp_archive=ezinsar.cli.ezinsarapp_archive:main',
                            'ezinsarapp_archive_decrypt=ezinsar.cli.ezinsarapp_archive_decrypt:main',
                            'ezinsarapp_3DdispSE=ezinsar.cli.ezinsarapp_3DdispSE:main',
                            'ezinsarapp_update=ezinsar.cli.ezinsarapp_update:main',
                            'ezinsarapp_docker=ezinsar.cli.ezinsarapp_docker:main',
                            'ezinsarapp_program=ezinsar.cli.ezinsarapp_program:main',
                            'ezinsarapp_docs=ezinsar.cli.ezinsarapp_docs:main',
                            'ezinsarapp_toolkit=ezinsar.cli.ezinsarapp_toolkit:main',
                            'ezinsarapp_job=ezinsar.cli.ezinsarapp_job:main',
                            'ezinsarapp_S1detect=ezinsar.cli.ezinsarapp_S1detect:main',
                            'ezinsarapp_S1mosaic=ezinsar.cli.ezinsarapp_S1mosaic:main',

                            # DEM interface 
                            'ezinsarapp_dem_master=ezinsar.cli.dem.ezinsarapp_dem_master:main',
                            'ezinsarapp_dem_list=ezinsar.cli.dem.ezinsarapp_dem_list:main',
                            'ezinsarapp_dem_checkext=ezinsar.cli.dem.ezinsarapp_dem_checkext:main',
                            'ezinsarapp_dem_tiles=ezinsar.cli.dem.ezinsarapp_dem_tiles:main',
                            'ezinsarapp_dem_download=ezinsar.cli.dem.ezinsarapp_dem_download:main',
                            'ezinsarapp_dem_merge=ezinsar.cli.dem.ezinsarapp_dem_merge:main',
                            'ezinsarapp_dem_mask=ezinsar.cli.dem.ezinsarapp_dem_mask:main',
                            'ezinsarapp_dem_replace=ezinsar.cli.dem.ezinsarapp_dem_replace:main',
                            'ezinsarapp_dem_ellcorr=ezinsar.cli.dem.ezinsarapp_dem_ellcorr:main',
                            'ezinsarapp_dem_translate=ezinsar.cli.dem.ezinsarapp_dem_translate:main',
                            'ezinsarapp_dem_run=ezinsar.cli.dem.ezinsarapp_dem_run:main',
                            ]},
    )