#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

import os
import subprocess
import pathlib

from ezinsardesktopmodule import __namePackage__ as project
from ezinsardesktopmodule import __copyrightPackage__ as copyright
from ezinsardesktopmodule import __versionPackage__ as version 
from ezinsardesktopmodule import __authorPackage__ as author

copyright = copyright.replace('Copyright','')

extensions = [
    "sphinx_rtd_theme",
    "sphinx.ext.intersphinx",
    "pydoctor.sphinx_ext.build_apidocs",
    "sphinxcontrib.spelling",
    "sphinxarg.ext",
    "nbsphinx",
    "myst_parser",
    "sphinx_tabs.tabs",
    'sphinxemoji.sphinxemoji',
]

nbsphinx_allow_errors = True
nbsphinx_execute = 'never'

templates_path = ['_templates']

exclude_patterns = []

rst_epilog = """
.. include:: <isonum.txt>
"""

spelling_word_list_filename = 'spelling_wordlist.txt'

intersphinx_mapping = {
    # FIXME: 
    'ezinsar': ('https://github.com/alexisInSAR/EZ-InSAR.git', None),
}

html_theme = "sphinx_rtd_theme"
html_logo = "private/EZ_InSAR_logo_desktop_whiteback.gif"
html_static_path = []

_git_reference = subprocess.getoutput('git rev-parse --abbrev-ref HEAD')
if _git_reference == 'HEAD':
    _git_reference = subprocess.getoutput('git rev-parse HEAD')

if os.environ.get('READTHEDOCS', '') == 'True':
    rtd_version = os.environ.get('READTHEDOCS_VERSION', '')
    if '.' in rtd_version:
        _git_reference = rtd_version

_ezinsar_root = pathlib.Path(__file__).parent.parent.parent
_common_args = [
    f'--html-viewsource-base=https://github.com/alexisInSAR/EZ-InSAR-Module-Desktop/tree/{_git_reference}',
    f'--project-base-dir={_ezinsar_root}', 
    f'--config={_ezinsar_root}/setup.cfg',
]
pydoctor_args = {
    'main': [
        '--html-output={outdir}/api/',
        '--project-name=EZ-InSAR Desktop Module',
        f'--project-version={version}',
        '--docformat=google', 
        '--intersphinx=https://docs.python.org/3/objects.inv',
        '--theme=readthedocs',
        '--project-url=../index.html',
        f'{_ezinsar_root}/src/ezinsardesktopmodule',
        ] + _common_args,
    }

pydoctor_url_path = {
    'main': '/en/{rtd_version}/api',
    }