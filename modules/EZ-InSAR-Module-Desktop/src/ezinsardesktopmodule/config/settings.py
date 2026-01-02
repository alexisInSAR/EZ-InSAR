import os 
import pandas as pd
import importlib
from ezinsardesktopmodule.config.themes import list_themes

if not os.path.isfile(os.path.expanduser("~")+os.sep+'.ezinsar'+os.sep+'config' + os.sep + 'desktop.config'): 
    with open(os.path.expanduser("~")+os.sep+'.ezinsar'+os.sep+'config' + os.sep + 'desktop.config','w') as fout:
        fout.write('theme::default\n')
        fout.write('docker_running::False\n')
        fout.write('UnlockTiles::False\n')
        fout.write('foliumCached::True\n')
        fout.write('plotlyCached::True\n')
        fout.write('Updatetime::0.5\n')
        fout.write('nbLineLog::1000\n')
        fout.write('Cputime::1000\n')

conf = pd.read_csv(os.path.expanduser("~")+os.sep+'.ezinsar'+os.sep+'config' + os.sep + 'desktop.config',delimiter='::',header=None,engine='python',names=['Variable','Value'])
themewanted = conf['Value'][0]
if not themewanted in list_themes: 
    themewanted = 'default'

__theme__ = eval("importlib.import_module('ezinsardesktopmodule.config.themes').%s" % (themewanted))
__docker_running__ = (conf['Value'][1] == 'True')
__UnlockTiles__ =  (conf['Value'][2] == 'True')
__foliumCached__ =  (conf['Value'][3] == 'True')
__plotlyCached__ =  (conf['Value'][4] == 'True')
__Updatetime__ = float(conf['Value'][5])
__nbLineLog__ = int(conf['Value'][6])
__Cputime__ = float(conf['Value'][7])

__usefullinks__ = {
    'Processor': {
        'ISCE-2': 'https://github.com/isce-framework/isce2',
        'Doris': 'http://doris.tudelft.nl/',
        'MintPy': 'https://github.com/insarlab/MintPy',
        'StaMPS': 'https://github.com/dbekaert/StaMPS',
        'MiaplPy': 'https://github.com/insarlab/MiaplPy',
        'SARvey': 'https://github.com/luhipi/sarvey',
        'SNAP': 'https://step.esa.int/main/download/snap-download/',
        'GAMMA': 'https://www.gamma-rs.ch/gamma-software',
        },
    'Sensor': {
        'Sentinel-1': 'https://sentinels.copernicus.eu/copernicus/sentinel-1',
        'TerraSAR-X': 'https://www.dlr.de/en/research-and-transfer/projects-and-missions/terrasar-x',
        'PAZ': 'https://www.hisdesat.es/en/paz/',
        'ALOS': 'https://www.eorc.jaxa.jp/ALOS/en/alos/a1_about_e.htm',
        'ALOS-2':'https://www.eorc.jaxa.jp/ALOS-2/en/about/palsar2.htm',
        'COSMO-SkyMed': 'https://www.asi.it/en/earth-science/cosmo-skymed/',
        },
    'Bugs': {
        'EZ-InSAR GitHub': 'https://github.com/alexisInSAR/EZ-InSAR',
        },
    'Others':{
        'Sentinel-1 MPC': 'https://sar-mpc.eu/',
        },
}
