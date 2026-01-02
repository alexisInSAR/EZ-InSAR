#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-
"""EZInSAR setuptools configuration"""

githublink='https://github.com/alexisInSAR/EZ-InSAR-3-Module-TSDisplayer.git'

from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open("README.rst", "r") as readme_file:
    readme = readme_file.read()


setup(name='EZ-InSAR TSDisplayer Module', 
    version='1.1.1', 
    author="Alexis Hrysiewicz UCD/iCRAG",
    author_email="alexis.hrysiewicz@ucd.ie",
    description="EZ-InSAR TSDisplayer Module",
    long_description_content_type="text/rst",
    long_description=readme,
    url=githublink,
    project_urls={
        'Repository': githublink,
        'Documentation': 'https://alexisinsar.github.io/EZ-InSAR-3-Module-TSDisplayer/',
        'Issue Tracker': 'https://github.com/alexisInSAR/EZ-InSAR-3-Module-TSDisplayer/issues',
    },
    packages=find_packages('ezinsartsdisplayermodule'),
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
            'console_scripts': ['ezinsartsdisplayer_run=ezinsartsdisplayermodule.TSDisplayerWidget:main',
                                ]},
)