#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to generate the Time series displayer

The module allows to generate the Time series displayer
    
    (From `ezinsar` package)

Changelog:
        * 1.0.0: Initial version, Mar. 2025

"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
colorscales = px.colors.named_colorscales()
import numpy as np 
import os

from ezinsar.tools import ezinsardata
from ezinsartsdisplayermodule import settings

listdata = ['LOS Displacement rate',
            'LOS Displacement',
            ]
            # 'UD Displacement rate',
            # 'UD Displacement',
            # 'EW Displacement rate',
            # 'EW Displacement',
            # 'NS Displacement rate',
            # 'NS Displacement']
# listdataunc = ['Uncertainty %s' % (x) for x in listdata]
# listdata = listdata + listdataunc

tilesfile = {'Name': ['OpenStreetMap'],'Tile': ['None'],'Contributors': ['None']}
if settings.__UnlockTiles__:
    from ezinsar import __file__
    with open(__file__.replace('__init__.py','3rdparty'+os.sep+'WMS'+os.sep+'foliumtiles.csv'),'r') as fconf:
        for lines in fconf.readlines():
            tilesfile['Name'].append(lines.split(' -/- ')[0].strip())
            tilesfile['Tile'].append(lines.split(' -/- ')[1].strip())
            tilesfile['Contributors'].append(lines.split(' -/- ')[2].strip())
    
################################################################################
## Class for each container
################################################################################
class mainwindow():

    def __init__(self,file=None,cachedir=None):
        
        self.file = file

        self.dataselection = None
        self.map = None
        self.ts = None
        self.tabmapconfig = None
        self.tabtslayout = None
        self.figmap = None
        self.figTS = None
        self.disabledoptionaltabs = (cachedir == None)

        self.createmap()
        self.createTSfigure()
        self.createmappart()
        self.createtspart()
        self.createtabmapconfig()
        self.cratetstablayout()
        
        self.layout = html.Div(
        children=[
            html.Div(
                className='container',
                children=[ 
                    dbc.Row([
                        dbc.Col([self.tabmapconfig],width=5),
                        dbc.Col([self.map],width=7),
                    ],style={'width':'100%'}),
                    dbc.Row([
                        dbc.Col([self.ts],width=8),
                        dbc.Col([self.tabtslayout],width=3),
                    ],style={'width':'100%', 'marginTop':15}),
                ])])

    ###############################################################
    ## Widget parts
    ###############################################################
    def createmappart(self): 
        """Create the map layout"""
        self.map = dbc.Row(
            [
                dbc.Col([
                    dcc.Graph(id='TS-displayer:map-figure',figure=self.figmap),
                    ],style={'width': '100%'}),
            ],style={'width': '100%'})
        
    def createtspart(self): 
        """Create the map layout"""
        self.ts = dbc.Tabs(
                [   
                # Tab for the time series plot 
                dbc.Tab(
                    [
                        dcc.Graph(id='TS-displayer:ts-plot',figure=self.createTSfigure())
                    ], 
                    label="Time Series", tab_id="TS-displayer:tabs-ts"),
                
                dbc.Tab(
                    [
                        dcc.Graph(id='TS-displayer:ts-plot2',figure=self.createTS2figure())
                    ], 
                    label="Other dataset(s)", tab_id="TS-displayer:tabs-ts2",disabled = self.disabledoptionaltabs),

                ],
                id="TS-displayer:tabs",
                active_tab="TS-displayer:tabs-ts",
                style={'marginTop': 100},
            )
        
    def createtabmapconfig(self): 
        tmp = []

        data = ezinsardata.loadEZdata(self.file,verbose=False,partialreading=['datainformation','dates'])

        for ki in list(data.datainformation.keys()):
            if not ki in ['Date','Metadata_processing','Importation','Path','Name']:
                tmpA = dbc.Row(
                    [
                    dbc.Col([dbc.Row([html.Div(children=['%s:' % (ki)], style={'fontSize': 12.5, 'fontWeight': 'bold', 'marginTop':10})])]),
                    dbc.Col([dbc.Row([html.Div(children=['%s' % (data.datainformation[ki])], style={'fontSize': 12.5, 'marginTop':10})])]),       
                    ], style={'width': '100%'})
                tmp.append(tmpA)

        # Dataset type  
        tmp.append(dbc.Row([
                    dbc.Col([dbc.Row([html.Div(children=['Selected data:'], style={'fontSize': 15, 'fontWeight': 'bold', 'marginTop':5})])]),
                    dbc.Col([dbc.Row([dcc.Dropdown(
                                id="TS-displayer:Dropdown-dataselected",
                                options=listdata,
                                value=listdata[0],
                                searchable=True,
                                clearable=False,
                            )
                            ]),
                            ]), 
            ],style={'width': '100%','marginTop': 10}))

        tab1 = dbc.Tab(label="Data Summary", 
                       tab_id="tab-data-selection",
                children=tmp,
                )
        
        tab2 = dbc.Tab(label="Map setting", 
                       tab_id="tab-map-configuration",
                children=[
                    
                    # dataset dates 
                    dbc.Row([
                            dbc.Col([dbc.Row([html.Div(children=['Selected date:'], style={'fontSize': 15, 'fontWeight': 'bold', 'marginTop':5})])]),
                            dbc.Col([dbc.Row([dcc.Dropdown(
                                        id="TS-displayer:Dropdown-dateselected",
                                        options=data.dates['value'],
                                        value=data.dates['value'][0],
                                        searchable=True,
                                        clearable=False,
                                        disabled = True,
                                    )
                                    ]),
                                    ]), 
                    ],style={'width': '100%','marginTop': 10}),

                    # Basemap
                    dbc.Row([
                        dbc.Col([dbc.Row([html.Div(children=['Basemap:'], style={'fontSize': 15, 'fontWeight': 'bold'})])]),
                        dbc.Col([dbc.Row([dcc.Dropdown(
                                    id="TS-displayer:Dropdown-basemap",
                                    options=tilesfile['Name'],
                                    value=tilesfile['Name'][0],
                                    searchable=True,
                                    clearable=False,
                        )
                        ]),
                        ]), 
                    ],style={'width': '100%','marginTop': 10}),

                    # Colormap
                    dbc.Row([
                        
                        dbc.Col([dbc.Row([html.Div(children=['Colormap:'], style={'fontSize': 15, 'fontWeight': 'bold'})])]),
                        dbc.Col([dbc.Row([dcc.Dropdown(
                                    id="TS-displayer:Dropdown-colormap",
                                    options=[{"value": x, "label": x} for x in colorscales],
                                    value='jet',
                                    searchable=True,
                                    clearable=False,
                        )
                        ]),
                        ]), 
                    ],style={'width': '100%','marginTop': 10}),

                    dbc.Row([
                        
                                dbc.Col([html.Div(children=['Point size:'], style={'fontSize': 15, 'fontWeight': 'bold'})]),
                                dbc.Col([dbc.Input(id="TS-displayer:ptsize", type="number", value=5, min=1, max=100)]),
                        
                        ],style={'width': '100%','marginTop': 10}),

                    # Colorscale limits
                    dbc.Row([
                        
                        dbc.Row([
                            html.Div(children=['Colorscale limits:'], style={'fontSize': 15, 'fontWeight': 'bold'}),
                        ],
                        style={'width': '100%','marginTop': 10}),
                        
                        dbc.Row([
                        
                            dbc.Col([dbc.Row([html.Div(children=['Min [mm/yr]:'], style={'fontSize': 15, 'fontWeight': 'normal'})])]),
                            dbc.Col([dbc.Row([dbc.Input(id="TS-displayer:cmin", type="number", value=-20)
                            ]),
                            ]), 
                        ],style={'width': '100%','marginTop': 10}),

                        dbc.Row([
                        
                            dbc.Col([dbc.Row([html.Div(children=['Max [mm/yr]:'], style={'fontSize': 15, 'fontWeight': 'normal'})])]),
                            dbc.Col([dbc.Row([dbc.Input(id="TS-displayer:cmax", type="number", value=20)
                            ]),
                            ]), 
                        ],style={'width': '100%','marginTop': 10}),

                      
                        

                    ],style={'width': '100%','marginTop': 10}),
                ],
                )
        
        self.tabmapconfig = dbc.Tabs(
            [
                tab1,
                tab2,
            ],
            id="tab-map",
            active_tab="tab-data-selection",
        )
        

    def cratetstablayout(self): 

        tab1 = dbc.Tab(label="Info.", 
                       tab_id="tab-point-information",
                children=[
                    dbc.Row([
                        dbc.Row([
                            dbc.Col(dbc.Label("Index of point:",style={'fontSize': '10px','fontWeight': 'bold'})), 
                            dbc.Col(dbc.Label("XXXXX",style={'fontSize': '10px'},id="TS-displayer:idxinfo"))],justify="between"),
                        dbc.Row([
                            dbc.Col(dbc.Label("Longitude:",style={'fontSize': '10px','fontWeight': 'bold'})), 
                            dbc.Col(dbc.Label("XXXXX",style={'fontSize': '10px'},id="TS-displayer:loninfo"))],justify="between"),
                        dbc.Row([
                            dbc.Col(dbc.Label("Latitude:",style={'fontSize': '10px','fontWeight': 'bold'})), 
                            dbc.Col(dbc.Label("XXXXX",style={'fontSize': '10px'},id="TS-displayer:latinfo"))],justify="between"),
                        dbc.Row([
                            dbc.Col(dbc.Label("Linear Rate:",style={'fontSize': '10px','fontWeight': 'bold'})), 
                            dbc.Col(dbc.Label("XXXXX",style={'fontSize': '10px'},id="TS-displayer:lininfo"))],justify="between"),
                        dbc.Row([
                            dbc.Col(dbc.Label("Quadratic Acceleration:",style={'fontSize': '10px','fontWeight': 'bold'})), 
                            dbc.Col(dbc.Label("XXXXX",style={'fontSize': '10px'},id="TS-displayer:quadinfo"))],justify="between"),
                        dbc.Row([
                            dbc.Col(dbc.Label("Quadratic Linear Rate:",style={'fontSize': '10px','fontWeight': 'bold'})), 
                            dbc.Col(dbc.Label("XXXXX",style={'fontSize': '10px'},id="TS-displayer:quadlininfo"))],justify="between"),
                        dbc.Row([
                            dbc.Col(dbc.Label("Half life:",style={'fontSize': '10px','fontWeight': 'bold'})), 
                            dbc.Col(dbc.Label("XXXXX",style={'fontSize': '10px'},id="TS-displayer:halflifeinfo"))],justify="between"),
                            ],
                        style={'width': '100%','marginTop': 10})
                    ],
                )
        
        tab2 = dbc.Tab(label='Tools', 
                       tab_id="tab-point-tools",
                children=[
                    # For the radius of selection
                    dbc.Row([
                        
                            dbc.Col([dbc.Row([html.Div(children=['Radius of selection [m]:'], style={'WordWrap': True, 'fontSize': 12.5, 'fontWeight': 'bold'})])]),
                            dbc.Col([dbc.Row([dbc.Input(id="TS-displayer:radius", type="number", value=50, min=1,step=1), 
                            ]),
                            ]), 
                        ],style={'width': '100%','marginTop': 10}),

                    # For the detrending
                    dbc.Row([
                            dcc.Checklist(id="TS-displayer:detrending",options=[{'label': ' Detrend the time series', 'value': 'detrendingTS'}],value=[''],style={'fontSize': '15px','fontWeight': 'normal'}),
                        ],style={'width': '100%','marginTop': 10}),


                    dbc.Row([
                            html.Button('Export the velocities of selected points', id='TS-displayer:export-bt',style={'width': '100%','fontSize': '12.5px','fontWeight': 'normal','WordWrap': True}),
                            dcc.ConfirmDialog(
                                id='TS-displayer:export-error',
                                message='Please use the selector, on the map, to select the points.',
                            ),
                            dcc.Download(id="TS-displayer:export-downloader"),
                        ],style={'width': '85%','marginTop': 10}),

                    dbc.Row([
                            html.Button('Export the selected time series', id='TS-displayer:exportTS-bt',style={'width': '100%','fontSize': '12.5px','fontWeight': 'normal','WordWrap': True}),
                        ],style={'width': '85%','marginTop': 10}),

                    ],
                )
        
        tab3 = dbc.Tab(label='Dataset(s)', 
                       tab_id="tab-point-otherdata",
                children=[
                    dbc.Row([dcc.Dropdown(
                                    id="TS-displayer:datasets-list",
                                    options=['No dataset'],
                                    value='No dataset',
                                    searchable=True,
                                    clearable=False)
                    ],style={'width': '85%','marginTop': 10}),

                    dbc.Row([
                        dcc.Upload(
                            id='TS-displayer:datasets-upload',
                            children=html.Div([
                                'Upload an EZ-InSAR dataset',
                            ]),
                            style={
                                'width': '100%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px'
                            },
                            # Allow multiple files to be uploaded
                            multiple=False
                        ),
                    ],style={'width': '85%','marginTop': 10}),

                    dbc.Row([
                        html.Button('Remove the EZ-InSAR dataset', id='TS-displayer:datasets-removebt',style={'width': '100%','fontSize': '15px','fontWeight': 'normal','WordWrap': True}),
                    ],style={'width': '85%','marginTop': 10}),
                    dbc.Row([
                        dcc.ConfirmDialog(
                                id='TS-displayer:datasets-error',
                                message='The file is not compatible with EZ-InSAR.',
                            ),
                    ],style={'width': '85%','marginTop': 10}),
                ],
                disabled = self.disabledoptionaltabs, 
                )

               
        self.tabtslayout = dbc.Tabs(
            [
                tab1,
                tab2,
                tab3,
            ],
            id="tab-ts",
            # active_tab="tab-ts",
            style={'marginTop': 50,'width': '100%'},
        )

    def createmap(self):
        ## Map initialisation
        self.figmap = go.Figure() 
        self.figmap.add_trace(go.Scattermap(lat=[0],lon=[0],mode='markers',name='Rates',showlegend=False,hoverinfo='none',
                marker=go.scattermap.Marker(
                    color=[0],
                    showscale=True,
                    colorscale='jet',
                    cmin= -20, 
                    cmax= +20, 
                    size=5)))
        
        if not self.file == None:
            data = ezinsardata.loadEZdata(self.file,verbose=False,partialreading=['lat','lon','lat_grid','lon_grid'])
           
            if data.getformat() == 'pt': 
                lat = data.lat['value']
                lon = data.lon['value']
            else: 
                lat = data.lat_grid['value'].flatten()
                lon = data.lon_grid['value'].flatten()

            max_bound = max(abs(np.max(lon)-np.min(lon)), abs(np.max(lat)-np.min(lat))) * 111
            zoom = 12 - np.log(max_bound)

        else:
            lat = [0,0,0]
            lon = [0,0,0]
            zoom = 0

        self.figmap.data[0].marker.colorbar.title = 'LOS Displacement Rate [mm/yr]'
        self.figmap.data[0].marker.colorbar.title.side = 'right'
        self.figmap.update_layout(
                coloraxis_colorbar_x=-0.15,
                margin ={'l':0,'t':0,'b':0,'r':0},
                map = {
                    'center': {'lon': np.nanmean(lon), 'lat': np.nanmean(lat)},
                    'style': "open-street-map",
                    'zoom': zoom},
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                autosize=True)

    def createTSfigure(self):
        ## Initialisation of the time series plot 
        t = np.linspace(0, 10, 100)
        y = np.sin(t)
        figTS = go.Figure(data=go.Scatter(x=None, y=None, mode='markers'))
        figTS.add_trace(go.Scatter(x=t, y=-y, mode='markers'))
        figTS.update_layout(
                margin ={'l':0,'t':0,'b':0,'r':0},
                autosize=True,
                height=200,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)')
        figTS.update_layout(legend=dict(y=0))
        figTS.update_xaxes(title="Time")
        figTS.update_yaxes(title="Displacements [mm]")

        return figTS
    
    def createTS2figure(self):
        ## Initialisation of the time series plot 
        t = np.linspace(0, 10, 100)
        y = np.sin(t)
        figTS2 = go.Figure(data=go.Scatter(x=None, y=None, mode='markers'))
        figTS2.add_trace(go.Scatter(x=t, y=-y, mode='markers'))
        figTS2.update_layout(
                margin ={'l':0,'t':0,'b':0,'r':0},
                autosize=True,
                height=200,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)')
        figTS2.update_layout(legend=dict(y=0))
        figTS2.update_xaxes(title="Time")
        figTS2.update_yaxes(title="Displacements [mm]")

        return figTS2

    
    