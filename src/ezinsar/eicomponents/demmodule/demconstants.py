#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module for the DEM information

The module lists the DEM information.

    (From `ezinsar` package)

Changelog:
        * 3.2.1: Initial version, Sep. 2025

"""
import datetime

__DEMinformation__ = {
        
        ################################################################
        'SRTM': 
                {'name': 'SRTM (legacy)',
                'key': 'SRTM',
                'provider': 'NASA via elevation package',
                'extent': 'Global',
                'extent_file': 'https://raw.githubusercontent.com/OpenTopography/Data_Catalog_Spatial_Boundaries/main/OpenTopography_Raster/SRTM_GL1.geojson',
                'description': 'SRTM consisted of a specially modified radar system that flew onboard the Space Shuttle Endeavour during an 11-day mission in February of 2000. SRTM is an international project spearheaded by the National Geospatial-Intelligence Agency (NGA) and the National Aeronautics and Space Administration (NASA).',
                'resolution [m]': 30,
                'horizontal ref.': 'WGS84 [EPSG: 4326]',
                'vertical ref.': 'WGS84 Ellipsoid/EGM1996 Geoid [EPSG: 5773]', 
                'unit': 'meter', 
                'access': 'without account',
                'survey date' : '02/11/2000 - 02/22/2000',
                'citation': 'NASA Shuttle Radar Topography Mission (SRTM)(2013). Shuttle Radar Topography Mission (SRTM) Global. Distributed by OpenTopography. https://doi.org/10.5069/G9445JDF. Accessed %s' % (datetime.datetime.now().strftime('%Y-%m-%d')),
                'license': 'Not Provided',
                },

        ################################################################        
        'NASADEM': 
                {'name': 'NASADEM',
                'key': 'NASADEM',
                'provider': 'NASA via OpenTopography',
                'extent': 'Global',
                'extent_file': 'https://raw.githubusercontent.com/OpenTopography/Data_Catalog_Spatial_Boundaries/main/OpenTopography_Raster/NASADEM.geojson',
                'description': 'NASADEM is a modernization of the Digital Elevation Model (DEM) and associated products generated from the Shuttle Radar Topography Mission (SRTM) data.',
                'resolution [m]': 30,
                'horizontal ref.': 'WGS84 [EPSG: 4326]',
                'vertical ref.': 'WGS84 Ellipsoid/EGM1996 Geoid [EPSG: 5773]', 
                'unit': 'meter', 
                'access': 'without account',
                'survey date' : '02/11/2000 - 02/21/2000',
                'citation': 'NASA JPL (2021). NASADEM Merged DEM Global 1 arc second V001. Distributed by OpenTopography. https://doi.org/10.5069/G93T9FD9. Accessed %s' % (datetime.datetime.now().strftime('%Y-%m-%d')),
                'license': 'Not Provided', 
                },

        ################################################################
        'Copernicus': 
                {'name': 'Copernicus GLO-30 Digital Elevation Model (legacy)',
                'key': 'Copernicus',
                'provider': 'ESA/DLR via OpenTopography',
                'extent': 'Global',
                'extent_file': 'https://raw.githubusercontent.com/OpenTopography/Data_Catalog_Spatial_Boundaries/main/OpenTopography_Raster/COP30.geojson',
                'description': 'The Copernicus DEM is a Digital Surface Model (DSM) which represents the surface of the Earth including buildings, infrastructure and vegetation. It is based on the radar satellite data acquired during the TanDEM-X Mission.',
                'resolution [m]': 30,
                'horizontal ref.': 'WGS84 [EPSG: 4326]',
                'vertical ref.': 'WGS84 Ellipsoid/EGM2008 Geoid [EPSG: 3855]', 
                'unit': 'meter', 
                'access': 'without account',
                'survey date' : '01/01/2011 - 07/01/2015',
                'citation': 'European Space Agency (2024). Copernicus Global Digital Elevation Model. Distributed by OpenTopography. https://doi.org/10.5069/G9028PQB. Accessed %s' % (datetime.datetime.now().strftime('%Y-%m-%d')),
                'license': '(c) DLR e.V. 2010-2014 and (c) Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved.',
                },

        ################################################################
        'Copernicus3': 
                {'name': 'Copernicus GLO-90 Digital Elevation Model (legacy)',
                'key': 'Copernicus3',
                'provider': 'ESA/DLR via OpenTopography',
                'extent': 'Global',
                'extent_file': 'https://raw.githubusercontent.com/OpenTopography/Data_Catalog_Spatial_Boundaries/main/OpenTopography_Raster/COP90.geojson',
                'description': 'The Copernicus DEM is a Digital Surface Model (DSM) which represents the surface of the Earth including buildings, infrastructure and vegetation. It is based on the radar satellite data acquired during the TanDEM-X Mission.',
                'resolution [m]': 90,
                'horizontal ref.': 'WGS84 [EPSG: 4326]',
                'vertical ref.': 'WGS84 Ellipsoid/EGM2008 Geoid [EPSG: 3855]', 
                'unit': 'meter', 
                'access': 'without account',
                'survey date' : '01/01/2011 - 07/01/2015',
                'citation': 'European Space Agency (2024). Copernicus Global Digital Elevation Model. Distributed by OpenTopography. https://doi.org/10.5069/G9028PQB. Accessed %s' % (datetime.datetime.now().strftime('%Y-%m-%d')),
                'license': '(c) DLR e.V. 2010-2014 and (c) Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved.',
                },

        ################################################################
        'AW3D30': 
                {'name': 'ALOS World 3D - 30m',
                'key': 'AW3D30',
                'provider': 'JAXA',
                'extent': 'Global',
                'extent_file': 'https://www.eorc.jaxa.jp/ALOS/jp/dataset/aw3d30/data/List_of_all_tiles_in_AW3D30.txt',
                'description': 'This data set is a global digital surface model (DSM) with horizontal resolution of approximately 30 meters (basically 1 arcsecond) by the Panchromatic Remote-sensing Instrument for Stereo Mapping (PRISM), which was an optical sensor on board the Advanced Land Observing Satellite "ALOS". ',
                'resolution [m]': 30,
                'horizontal ref.': 'WGS84 [EPSG: 4326]',
                'vertical ref.': 'WGS84 Ellipsoid/EGM1996 Geoid [EPSG: 5773]', 
                'unit': 'meter', 
                'access': 'with account',
                'survey date' : '01/01/2006 - 01/01/2011',
                'citation': 'J. Takaku, T. Tadono, K. Tsutsui : Generation of High Resolution Global DSM from ALOS PRISM, The International Archives of the Photogrammetry, Remote Sensing and Spatial Information Sciences, pp.243-248, Vol. XL-4, ISPRS TC IV Symposium, Suzhou, China, 2014.',
                'license': 'Any of the commercial and non-commercial purposes can be used free of charge under the conditions of the "5. Terms of Use" below',
                },

        ################################################################
        'RGEALTI-1m': 
                {'name': 'RGEALTI DTM - 1m',
                'key': 'RGEALTI-1m',
                'provider': 'IGN',
                'extent': 'French territories',
                'extent_file': None,
                'description': 'This data is the French DTM based on various methods (LiDAR, stereo-photogrammetry, etc.).',
                'resolution [m]': 1,
                'horizontal ref.': 'Variable',
                'vertical ref.': 'IAG GRS 1980', 
                'unit': 'meter', 
                'access': 'without account',
                'survey date' : None,
                'citation': None,
                'license': '?????',
                },

        ################################################################
        'RGEALTI-5m': 
                {'name': 'RGEALTI DTM - 5m',
                'key': 'RGEALTI-5m',
                'provider': 'IGN',
                'extent': 'French territories',
                'extent_file': None,
                'description': 'This data is the French DTM based on various methods (LiDAR, stereo-photogrammetry, etc.).',
                'resolution [m]': 5,
                'horizontal ref.': 'Variable',
                'vertical ref.': 'IAG GRS 1980', 
                'unit': 'meter', 
                'access': 'without account',
                'survey date' : None,
                'citation': None,
                'license': '?????',
                },

        ################################################################
        'COPDEM30': 
                {'name': 'Copernicus GLO-30 Digital Elevation Model',
                'key': 'COPDEM30',
                'provider': 'ESA/DLR via Copernicus Data Space',
                'extent': 'Global',
                'extent_file': None,
                'description': 'The Copernicus DEM is a Digital Surface Model (DSM) which represents the surface of the Earth including buildings, infrastructure and vegetation. It is based on the radar satellite data acquired during the TanDEM-X Mission.',
                'resolution [m]': 30,
                'horizontal ref.': 'WGS84 [EPSG: 4326]',
                'vertical ref.': 'WGS84 Ellipsoid/EGM2008 Geoid [EPSG: 3855]', 
                'unit': 'meter', 
                'access': 'without account',
                'survey date' : '01/01/2011 - 07/01/2015',
                'citation': 'The GLO-30 and GLO-90 datasets are available worldwide with a free license. ESA - EU users who use the Copernicus DEM in their research are requested to use the following DOI when citing the data source in their publications: https://doi.org/10.5270/ESA-c5d3d65',
                'license': '(c) DLR e.V. 2010-2014 and (c) Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved',
                },

        ################################################################
        'COPDEM90': 
                {'name': 'Copernicus GLO-90 Digital Elevation Model',
                'key': 'COPDEM90',
                'provider': 'ESA/DLR via Copernicus Data Space',
                'extent': 'Global',
                'extent_file': None,
                'description': 'The Copernicus DEM is a Digital Surface Model (DSM) which represents the surface of the Earth including buildings, infrastructure and vegetation. It is based on the radar satellite data acquired during the TanDEM-X Mission.',
                'resolution [m]': 90,
                'horizontal ref.': 'WGS84 [EPSG: 4326]',
                'vertical ref.': 'WGS84 Ellipsoid/EGM2008 Geoid [EPSG: 3855]', 
                'unit': 'meter', 
                'access': 'without account',
                'survey date' : '01/01/2011 - 07/01/2015',
                'citation': 'The GLO-30 and GLO-90 datasets are available worldwide with a free license. ESA - EU users who use the Copernicus DEM in their research are requested to use the following DOI when citing the data source in their publications: https://doi.org/10.5270/ESA-c5d3d65',
                'license': '(c) DLR e.V. 2010-2014 and (c) Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved',
                },

        ################################################################
        'perso': 
                {'name': 'Personal DEM',
                'key': 'perso',
                'provider': None,
                'extent': None,
                'extent_file': None,
                'description': None,
                'resolution [m]': None,
                'horizontal ref.': None,
                'vertical ref.': None,
                'unit': None,
                'access': None,
                'survey date': None,
                'citation': None,
                'license': None,
                },
}