import os 

if not os.path.isfile(os.path.expanduser("~")+os.sep+'.ezinsar'+os.sep+'config' + os.sep + 'tsdiplayer.config'): 
    with open(os.path.expanduser("~")+os.sep+'.ezinsar'+os.sep+'config' + os.sep + 'tsdiplayer.config','w') as fout:
        fout.write('UnlockTiles::True\n')
      
conf = {'Variable': [],'Value': []}
with open(os.path.expanduser("~")+os.sep+'.ezinsar'+os.sep+'config' + os.sep + 'tsdiplayer.config','r') as fconf:
    for lines in fconf.readlines():
        conf['Variable'].append(lines.split('::')[0].strip())
        conf['Value'].append(lines.split('::')[-1].strip())

__UnlockTiles__ = (conf['Value'][0] == 'True')
