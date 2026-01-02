#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to build the EZ-InSAR Time series Displayer

The module allows to generate the EZ-InSAR GUI (main part)
    
    (Supplementary module for EZ-InSAR)

Changelog:
        * 1.0.0: Initial version, Mar. 2025

"""

################################################################################
## Python packages
################################################################################
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import logging

from ezinsartsdisplayermodule import widgets

################################################################################
## Create the application 
################################################################################
class TSDisplayerserver():

    def __init__(self,pathfile=None,cachedir=None):

        self.app = Dash(
            __name__,
            meta_tags=[
                {'charset': 'utf-8'},
                {'name': 'viewport',
                'content': 'width=device-width, initial-scale=1, shrink-to-fit=yes', 
                }
                ],
                external_stylesheets=[dbc.themes.BOOTSTRAP], 
            )

        ## Some variables 
        self.app.jobfile = 'dummy.ei'
        self.app.title='EZ-InSAR - Time series Displayer'
        self.app.update_title='EZ-InSAR: running in progress...'
        self.app._favicon = 'EZ_InSAR_logo_tsdisplayer_whiteback.svg'

        ## Other datasets
        self.app.listotherdata = [] 
    
        ## Load the dataset
        self.app.data = pathfile
        self.app.cachedir = cachedir
        
        ## Assembly the layout
        maingui = widgets.mainwindow(file=self.app.data,cachedir=self.app.cachedir)
        self.app.layout = html.Div(
            [ 
                maingui.layout,
                dcc.Store(id='tsdisplayer-data:jobfile', storage_type='memory', data=self.app.jobfile),
                dcc.Store(id='tsdisplayer-data:data', storage_type='memory', data=self.app.data),
                dcc.Store(id='tsdisplayer-data:listotherdata', storage_type='memory', data=self.app.listotherdata),
                dcc.Store(id='tsdisplayer-data:cachedir', storage_type='memory', data=self.app.cachedir),
            ]
        )

        logflask = logging.getLogger('werkzeug')
        logflask.disabled = True

        ################################################################################
        ## Import the callbacks
        ################################################################################
        from ezinsartsdisplayermodule import callbacks
        callbacks.get_callbacks(self.app)

def startWebserver(file,host,port,cachedir_obs):
        object = TSDisplayerserver(pathfile=file,cachedir=cachedir_obs)
        object.app.run(host=host,port=port,debug=False, use_reloader=False)

## For debug 
if __name__ == '__main__':
    object = TSDisplayerserver(pathfile='test.eidata')
    object.app.run(debug=True, use_reloader=True)