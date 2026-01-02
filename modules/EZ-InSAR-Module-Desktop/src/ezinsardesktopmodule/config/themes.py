import glob, os 
from datetime import datetime

def read_qss(file): 
    base_path = os.path.dirname(file)
    with open(file,'r') as fi:
        text = fi.read()
        text = text.replace("url(", f"url({base_path}%s" % (os.sep))
    return text

############################################
list_themes = ['default','EZInSAR_auto','EZInSAR_light','EZInSAR_dark'] 

############################################
default = """"""

############################################
EZInSAR_light = read_qss(__file__.replace('themes.py','QSSthemes%sEZInSAR_light.qss' % (os.sep)))
EZInSAR_dark = read_qss(__file__.replace('themes.py','QSSthemes%sEZInSAR_dark.qss' % (os.sep)))

if (datetime.today().hour > 22) and (datetime.today().hour < 5): 
    EZInSAR_auto = EZInSAR_dark
else: 
    EZInSAR_auto = EZInSAR_light
