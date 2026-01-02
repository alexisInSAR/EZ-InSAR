#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Callbacks for the Time series displayer

Callbacks for the Time series displayer
    
    (From `ezinsar` package)

Changelog:
        * 1.0.0: Initial version, Mar. 2025

"""

################################################################################
## Python packages
################################################################################
## Packages in relation to dash
from dash import Output, Input, State, ctx, dcc

from ezinsar.tools import ezinsardata
from ezinsar.constants import __cachedir__
from ezinsartsdisplayermodule import settings

import plotly.graph_objs as go
import numpy as np
import scipy.optimize as opt
import os
import zipfile
import glob
import base64
import datetime
import pandas as pd

################################################################################
## Builder
################################################################################
def get_callbacks(app):
    """EZ-InSAR GUI callback builder: satellite parameters

    The function contains the callbacks of the EZ-InSAR GUI for the satellite parameters.

    Args: 
        app (``ezinsar app``): EZ-InSAR Dash application

    """

    #############################################################
    ## updatamap
    #############################################################
    @app.callback(
        [Output('TS-displayer:map-figure', 'figure'), 
        Output('TS-displayer:Dropdown-dateselected', 'disabled')],
        [Input("TS-displayer:Dropdown-basemap", "value"),
        Input("TS-displayer:Dropdown-colormap", "value"),
        Input("TS-displayer:cmin", "value"),
        Input("TS-displayer:cmax", "value"),
        Input("TS-displayer:ptsize", "value"),
        Input("TS-displayer:Dropdown-dataselected", "value"),
        Input("TS-displayer:Dropdown-dateselected", "value")],
        [State('TS-displayer:map-figure', 'figure'),
        State('TS-displayer:Dropdown-dateselected', 'disabled'),
        State('TS-displayer:Dropdown-dateselected', 'value'),
        State("tsdisplayer-data:data", "data")],
    )
    def updatamap( 
            basemapvalue,
            colormapvalue,
            cmin,
            cmax,
            ptsize,
            dataselection,     
            dateselection, 
            figuremap,
            datepickerdisabled,
            datepickervalue,
            inputdata):
        """Callback for updating map
        """ 
        figuremap = go.Figure(figuremap)
        if ctx.triggered_id == 'TS-displayer:Dropdown-basemap':

            source = None
            if not basemapvalue == 'OpenStreetMap':
                tilesfile = {'Name': [],'Tile': [],'Contributors': []}
                from ezinsar import __file__
                with open(__file__.replace('__init__.py','3rdparty'+os.sep+'WMS'+os.sep+'foliumtiles.csv'),'r') as fconf:
                    for lines in fconf.readlines():
                        tilesfile['Name'].append(lines.split(' -/- ')[0].strip())
                        tilesfile['Tile'].append(lines.split(' -/- ')[1].strip())
                        tilesfile['Contributors'].append(lines.split(' -/- ')[2].strip())
                idx = tilesfile['Name'].index(basemapvalue)

                source = "%s" % (tilesfile['Tile'][idx])
                source = [source.replace('http://','https://').replace('http://services.arcgisonline.com/ArcGIS/','https://server.arcgisonline.com/ArcGIS/').replace('https://services.arcgisonline.com/ArcGIS/','https://server.arcgisonline.com/ArcGIS/')]

                figuremap.update_layout(
                    map = {'style': "white-bg"},
                    map_layers=[
                        {"below": 'traces',
                        "sourcetype": "raster",
                        "sourceattribution": "%s" % (' '.join(x for x in tilesfile['Contributors'][idx].split() if not x.startswith('&'))),
                        "source": source},
                    ])
            else:
                figuremap.update_layout(
                    map = {'style': "open-street-map"})

            return figuremap, datepickerdisabled
        
        elif ctx.triggered_id == 'TS-displayer:Dropdown-colormap':
            figuremap.data[0].marker.colorscale=colormapvalue

            return figuremap, datepickerdisabled
        
        elif ctx.triggered_id == 'TS-displayer:cmin' or ctx.triggered_id == 'TS-displayer:cmax' or ctx.triggered_id == 'TS-displayer:ptsize':
            figuremap.data[0].marker.cmin=cmin
            figuremap.data[0].marker.cmax=cmax
            figuremap.data[0].marker.size = ptsize

            return figuremap, datepickerdisabled
        
        if ctx.triggered_id in ['TS-displayer:Dropdown-dataselected','TS-displayer:Dropdown-dateselected']:
            data = ezinsardata.loadEZdata(inputdata,verbose=False,partialreading=['lon','rateLOS','dispLOS','dates'])
            idxselected =[x.strftime('%Y-%m-%dT%H:%M:%S') for x in data.dates['value']].index(datepickervalue)

            if dataselection == 'LOS Displacement rate':
                if data.getformat() == 'pt':  # For point data
                    ptdata = data.rateLOS['value']
                else: # For raster data
                    ptdata = np.flipud(data.rateLOS['value']).flatten()

                datepickerdisabled = True
                figuremap.data[0].marker.colorbar.title = 'LOS Displacement rate [mm/yr]'
                figuremap.data[0].marker.colorbar.title.side = 'right'

            else:
                if data.getformat() == 'pt':  # For point data
                    ptdata = data.dispLOS['value'][:,idxselected]
                else: # For raster data
                    ptdata = np.flipud(data.dispLOS['value'][:,:,idxselected]).flatten()

                datepickerdisabled = False
                figuremap.data[0].marker.colorbar.title = '%s [mm]' % (dataselection)
                figuremap.data[0].marker.colorbar.title.side = 'right'

            figuremap.data[0].marker.color = ptdata[~np.isnan(ptdata)]

            return figuremap, datepickerdisabled
        
        else:
            data = ezinsardata.loadEZdata(inputdata,verbose=False,partialreading=['datainformation','lat','lon','lat_grid','lon_grid','rateLOS'])
            
            if data.getformat() == 'pt':  # For point data
                lat = data.lat['value']
                lon = data.lon['value']
                ptdata = data.rateLOS['value']
            else: # For raster data
                lat = data.lat_grid['value'].flatten()
                lon = data.lon_grid['value'].flatten()
                ptdata = np.flipud(data.rateLOS['value']).flatten()

            figuremap.data[0].lat = lat[~np.isnan(ptdata)]
            figuremap.data[0].lon = lon[~np.isnan(ptdata)]
            figuremap.data[0].marker.color = ptdata[~np.isnan(ptdata)]

            max_bound = max(abs(np.max(lon)-np.min(lon)), abs(np.max(lat)-np.min(lat))) * 111
            figuremap.update_layout(mapbox = {
                                        'center': {'lat': np.nanmean(lat), 'lon': np.nanmean(lon)},
                                        'zoom': 11.5 - np.log(max_bound),
                                        },             
                                    )

        return figuremap, datepickerdisabled
        
    #############################################################
    ## callbackupdateTS
    #############################################################
    @app.callback(
        [Output('TS-displayer:ts-plot', 'figure'),
        Output('TS-displayer:ts-plot2', 'figure'),
        Output('TS-displayer:idxinfo', 'children'),
        Output('TS-displayer:loninfo', 'children'),
        Output('TS-displayer:latinfo', 'children'),
        Output('TS-displayer:lininfo', 'children'),
        Output('TS-displayer:quadinfo', 'children'),
        Output('TS-displayer:quadlininfo', 'children'),
        Output("TS-displayer:halflifeinfo",'children')],
        Input('TS-displayer:map-figure','clickData'),
        Input('TS-displayer:map-figure','selectedData'),
        Input('TS-displayer:detrending', 'value'),
        Input("TS-displayer:radius", 'value'),
        [State('TS-displayer:ts-plot', 'figure'),
        State('TS-displayer:ts-plot2', 'figure'),
        State("tsdisplayer-data:data", "data"),
        State("tsdisplayer-data:cachedir", "data"),
        State('tsdisplayer-data:listotherdata', 'data')],
    )
    def callbackupdateTS(clickData, 
            selectedData,
            detrendingvalue,
            selectionradius,
            figureTS,figureTS2,inputdata,
            cachedir,
            listdataset):
        """Callback for opening the map
        """ 
        figureTS = go.Figure()
        figureTS2 = go.Figure()
        
        if ctx.triggered_id in ['TS-displayer:map-figure', 'TS-displayer:detrending', 'TS-displayer:radius']:
            ## Extraction of time series 
            data = ezinsardata.loadEZdata(inputdata,verbose=False,partialreading=['datainformation','lat','lon','lat_grid','lon_grid','x_utm','y_utm','dispLOS','dates','code_meter'])

            # For point data
            if not selectedData == None:
                idx = []
                for pti in selectedData['points']:
                    idx.append(pti['pointIndex'])
            elif not clickData == None: 
                idx = clickData['points'][0]['pointIndex']

            try: 
                _, ydisp, _ = data.extractts(0,0,radius=selectionradius,idx_pts=idx)
            except: 
                ydisp = np.array([None])
 
            if not ydisp.any() == None:
                figureTS.data = []
                figureTS2.data = []

                ## Modification if detrending 
                xtemp = []
                for ti in data.dates['value']:
                    xtemp.append(ti.timestamp())

                if 'detrendingTS' in detrendingvalue:
                    m1, v1 = np.polyfit(xtemp-np.mean(xtemp), ydisp, 1, cov=True)
                    ydisp = (ydisp - np.polyval(m1,np.array(xtemp)-np.mean(xtemp)))
                
                figureTS.add_trace(go.Scatter(
                    x=data.dates['value'],
                    y=ydisp,
                    name ='InSAR observations',  mode='markers'))
                
                figureTS2.add_trace(go.Scatter(
                    x=data.dates['value'],
                    y=ydisp,
                    name ='Orignal dataset',  mode='markers'))
                
                ## Check if other datasets are available 
                for datai in listdataset:

                    if not clickData == None: 
                        lonpt = clickData['points'][0]['lon']
                        latpt = clickData['points'][0]['lat']

                        databis = ezinsardata.loadEZdata(cachedir+os.sep+datai,verbose=False,partialreading=['datainformation','lat','lon','lat_grid','lon_grid','x_utm','y_utm','dispLOS','dates','code_meter'])
                        _, ydisp2, _ = databis.extractts(lonpt,latpt,radius=selectionradius)
                        try: 
                            _, ydisp2, _ = databis.extractts(lonpt,latpt,radius=selectionradius)
                        except: 
                            date2 = databis.dates['value']
                            ydisp2 = np.array([None])

                        if not ydisp.any() == None:
                            if 'detrendingTS' in detrendingvalue:
                                xtemp = []
                                for ti in databis.dates['value']:
                                    xtemp.append(ti.timestamp())
                                m1, v1 = np.polyfit(xtemp-np.mean(xtemp), ydisp2, 1, cov=True)
                                ydisp2 = (ydisp2 - np.polyval(m1,np.array(xtemp)-np.mean(xtemp)))

                            figureTS2.add_trace(go.Scatter(
                                x=databis.dates['value'],
                                y=ydisp2,
                                name = datai,  mode='markers'))



                                
                ## Computation of trends on-the-fly if optional module is available 
                try:
                    from ezinsarpostprocessingmodule.regression import fit 

                    polyres1 = fit.fit(data.dates['value'],ydisp).fitlinear()
                    lininfo = "%.3f mm/yr" % (polyres1.coeff[0]*365.25*24*3600)
                    figureTS.add_trace(go.Scatter(x=data.dates['value'], 
                        y=polyres1.ymod, 
                        name ='Linear evolution',  mode='lines', visible='legendonly'))
                    
                    polyres2 = fit.fit(data.dates['value'],ydisp).fitquad()
                    quadinfo = "%.3f mm/yr2" % (polyres2.coeff[0]*365.25*24*3600)
                    quadlininfo = "%.3f mm/yr" % (polyres2.coeff[1]*365.25*24*3600)
                    figureTS.add_trace(go.Scatter(x=data.dates['value'], 
                        y=polyres2.ymod, 
                        name ='Quadratic evolution',  mode='lines', visible='legendonly'))
                    
                    expfit1 = fit.fit(data.dates['value'],ydisp).fitexp()
                    if expfit1.success: 
                        halflifeinfo = "%.3f 1/yr" % (np.log(2)/(-expfit1.coeff[1]*365.25))
                        figureTS.add_trace(go.Scatter(x=data.dates['value'], 
                            y=expfit1.ymod, 
                            name ='Exponential evolution',  mode='lines', visible='legendonly'))
                    else:
                        halflifeinfo = 'NaN'

                except:
                    a = 'dummy'
                    lininfo = 'NaN'
                    quadinfo = 'NaN'
                    quadlininfo = 'NaN'
                    halflifeinfo = 'NaN'

                if not selectedData == None:
                    idxinfo = 'NaN'
                    loninfo = 'NaN'
                    latinfo = 'NaN'
                elif not clickData == None: 
                    idxinfo = clickData['points'][0]['pointIndex']
                    loninfo = "%.3f" % (clickData['points'][0]['lon'])
                    latinfo = "%.3f" % (clickData['points'][0]['lat'])

            else: 
                figureTS.data = []
                figureTS2.data = []
                idxinfo = 'NaN'
                loninfo = 'NaN'
                latinfo = 'NaN'
                lininfo = 'NaN'
                quadinfo = 'NaN'
                quadlininfo = 'NaN'
                halflifeinfo = 'NaN'
        
        else: 
            figureTS.data = []
            figureTS2.data = []
            idxinfo = 'NaN'
            loninfo = 'NaN'
            latinfo = 'NaN'
            lininfo = 'NaN'
            quadinfo = 'NaN'
            quadlininfo = 'NaN'
            halflifeinfo = 'NaN'

        figureTS.update_layout(
                margin ={'l':0,'t':0,'b':0,'r':0},
                autosize=True,
                height=200,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)')
        figureTS.update_layout(legend=dict(y=0))
        figureTS.update_xaxes(title="Time")
        figureTS.update_yaxes(title="Displacements [mm]")

        figureTS2.update_layout(
                margin ={'l':0,'t':0,'b':0,'r':0},
                autosize=True,
                height=200,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)')
        figureTS2.update_layout(legend=dict(y=0))
        figureTS2.update_xaxes(title="Time")
        figureTS2.update_yaxes(title="Displacements [mm]")

        return figureTS, figureTS2, idxinfo, loninfo, latinfo, lininfo, quadinfo, quadlininfo, halflifeinfo

    #############################################################
    ## callbackexportselection
    #############################################################
    @app.callback(
        [Output('TS-displayer:export-error', 'displayed'),
        Output('TS-displayer:export-downloader', 'data')],
        [Input('TS-displayer:export-bt', 'n_clicks'),
        Input('TS-displayer:exportTS-bt', 'n_clicks')],
        [State('TS-displayer:map-figure','selectedData'),
        State('TS-displayer:map-figure','clickData'),
        State("tsdisplayer-data:data", "data"),
        State('TS-displayer:ts-plot', 'figure')],
    )

    def callbackexportselection(btclick, btclick2, 
            selectedData,clickedData,inputdata,figureState,
            prevent_initial_call=True):
        """Export callback
        """ 
        if ctx.triggered_id in ['TS-displayer:export-bt']:

            if selectedData == None: 
                return True, None,
            else: 
                
                data = ezinsardata.loadEZdata(inputdata,verbose=False)

                ## Compute the region of interest based on selected points
                idx = []
                for pti in selectedData['points']:
                    idx.append(pti['pointIndex'])
                
                roicrop = data.getextent(idx_pts=idx)

                ezinsardata.exportEZdata(data,
                        __cachedir__+os.sep+'velocity.shp',
                        variable = ['rateLOS'],
                        format = 'ESRI Shapefile',
                        roi = roicrop, 
                        verbose = False, 
                )

                listfile = glob.glob(__cachedir__+os.sep+'velocity.*')
                with zipfile.ZipFile(__cachedir__+os.sep+'velocity.zip', "w") as fzip: 
                    for li in listfile: 
                        fzip.write(li,os.path.basename(li))

                for li in listfile: 
                    if os.path.isfile(li): 
                        os.remove(li)

                with open(__cachedir__+os.sep+'velocity.zip', 'rb') as file_data:
                    bytes_content = file_data.read()

                if os.path.isfile(__cachedir__+os.sep+'velocity.zip'): 
                        os.remove(__cachedir__+os.sep+'velocity.zip')

                return False, dcc.send_bytes(bytes_content,'velocity.zip')
            
        elif ctx.triggered_id in ['TS-displayer:exportTS-bt']:

            if clickedData == None: 
                return True, None
            else:                
                datasinglePT= ezinsardata.insitu()
                datasinglePT.data['value'] = pd.DataFrame.from_dict({'date': [datetime.datetime.strptime(xi, '%Y-%m-%dT%H:%M:%S') for xi in figureState['data'][0]['x']], 
                                                                    'displacement': figureState['data'][0]['y'],
                                                                    })
                datasinglePT.lon['value'] = clickedData['points'][0]['lon']
                datasinglePT.lat['value'] = clickedData['points'][0]['lat']
                datasinglePT.datainformation = {'Name': 'Extraction PT from %s' % (inputdata.split(os.sep)[-1]), 
                                'Original file': inputdata, 
                                'Short Description': 'Time series extracted from %s' % (inputdata.split(os.sep)[-1]), 
                                'Long Description': None, 
                                'EPSG_secondary': None, 
                                'Data Header': ['date','displacement'], 
                                'Data Unit': ['date','mm'], 
                                }
                
                ezinsardata.saveEZdata(datasinglePT, 
                                    __cachedir__+os.sep+'tmp.eidata',
                                    verbose = False)
                
                with open(__cachedir__+os.sep+'tmp.eidata', 'rb') as file_data:
                    bytes_content = file_data.read()

                if os.path.isfile(__cachedir__+os.sep+'tmp.eidata'): 
                        os.remove(__cachedir__+os.sep+'tmp.eidata')

                return False, dcc.send_bytes(bytes_content,'TSsinglepoint.eidata')
                        
        else: 
            return False, None

    #############################################################
    ## callbackimportdataset
    #############################################################
    @app.callback(
        [Output("tsdisplayer-data:listotherdata", "data"),
        Output('TS-displayer:datasets-list', 'options'),
        Output('TS-displayer:datasets-list', 'value'),
        Output('TS-displayer:datasets-error', 'displayed')],
        [Input('TS-displayer:datasets-upload', 'contents'),
         Input('TS-displayer:datasets-removebt', 'n_clicks'),
        Input('TS-displayer:datasets-upload', 'filename')],
        [State("tsdisplayer-data:listotherdata", "data"),
         State("tsdisplayer-data:cachedir", "data"),
         State('TS-displayer:datasets-list', 'value'),],
    )

    def callbackimportdataset(
            contentuploaded,
            btcliked,
            filenameuploaded,
            listdata,cachedir,
            valueinput,
            prevent_initial_call=True):
        """import callback
        """ 
        if ctx.triggered_id in ['TS-displayer:datasets-upload']:

            content_type, content_string = contentuploaded.split(',')
            decoded = base64.b64decode(content_string)
        
            if not os.path.isdir(cachedir):
                os.mkdir(cachedir)

            with open(cachedir+os.sep+filenameuploaded,'wb') as fout:
                fout.write(decoded)

            del decoded, content_type, content_string

            ## Test
            try:
                datetmp = ezinsardata.loadEZdata(cachedir+os.sep+filenameuploaded,verbose=False,partialreading=['datainformation'])
                if listdata:
                    listdata.append(filenameuploaded)
                else:
                    listdata = [filenameuploaded]
            
                if listdata:
                    opt = listdata
                    val = listdata[0]

                else:
                    opt = ['No dataset']
                    val = 'No dataset'

                return listdata, opt, val, False
            
            except:
                return listdata, listdata, listdata[0], True
            
        elif ctx.triggered_id in ['TS-displayer:datasets-removebt']:

            if not valueinput == 'No dataset':
                if os.path.isfile(cachedir+os.sep+valueinput):
                    os.remove(cachedir+os.sep+valueinput)
                    listdata.remove(valueinput)

            if not listdata:
                opt = ['No dataset']
                val = 'No dataset'
            else:
                opt = listdata
                val = listdata[0]

                
            return listdata, opt, val, False

        else: 
            return listdata, ['No dataset'], 'No dataset', False
        

