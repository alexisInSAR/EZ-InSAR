#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

##########################################################################################
# Header information 
###########################################################################

"""read_ALOS2_extent.py: Script to read the ALOS-2 StripMap extents"""

__author__ = "Alexis Hrysiewicz"
__copyright__ = "read_ALOS2_extent.py is part of EZ-InSAR toolbox"
__credits__ = ["Alexis Hrysiewicz"]
__license__ = "GPLV3"
__version__ = "1.0.0 Beta"
__maintainer__ = "Alexis Hrysiewicz"
__email__ = "alexis.hrysiewicz@ucd.ie"
__status__ = "Test"
__date__ = "Aug. 2024"

###########################################################################
# Python packages
###########################################################################
import sys
import os
import os.path
import optparse
import numpy as np
import glob
import struct
from shapely.geometry import Polygon
from scipy.spatial import ConvexHull

###########################################################################
class OptionParser (optparse.OptionParser):
    def check_required(self, opt):
        option = self.get_option(opt)
        if getattr(self.values, option.dest) is None:
            self.error("%s option not supplied" % option)
###########################################################################
if '-h' in sys.argv or '--help' in sys.argv:
    print("example: python3 %s -f file" %
          sys.argv[0])
    print("or\nexample: python3 %s -h [--help]" % sys.argv[0])
    print('HELP:')
    print('\t-f [--file]: ALOS-2 directory')

    sys.exit(-1)


parser = OptionParser()
parser.add_option("-f", "--file", dest="file", action="store", type="string", default='.')      
(options, args) = parser.parse_args()

###########################################################################
# Main function
###########################################################################
file = options.file

# If the file is provided by ASF
fileLED = glob.glob(file+os.sep+'LED*')[0]
fileVOL = glob.glob(file+os.sep+'VOL*')[0]
fileTRL = glob.glob(file+os.sep+'TRL*')[0]
fileIMG = glob.glob(file+os.sep+'IMG*')
fileSUM = glob.glob(file+os.sep+'summary*')[0]
fileXML = None

data_xml = dict()        

########################################
## Tie-points
try: 
    with open(fileIMG[0],'rb') as file:
        file.seek(237)
        SLCnblines = int(struct.unpack_from("8s",file.read(8))[0].decode('utf-8').split()[0])
    with open(fileIMG[0],'rb') as file:
        file.seek(281)
        SLCnbcols = int(struct.unpack_from("8s",file.read(8))[0].decode('utf-8').split()[0])
except:
    with open(fileIMG[-1],'rb') as file:
        file.seek(237)
        SLCnblines = int(struct.unpack_from("8s",file.read(8))[0].decode('utf-8').split()[0])
    with open(fileIMG[-1],'rb') as file:
        file.seek(281)
        SLCnbcols = int(struct.unpack_from("8s",file.read(8))[0].decode('utf-8').split()[0])
        
SLCnbcols = SLCnbcols / 8

# factor_undersampling_tiept = 100
# l = np.arange(0, SLCnblines, factor_undersampling_tiept)
# p = np.arange(0, SLCnbcols, factor_undersampling_tiept)
l = np.round(np.linspace(0, SLCnblines, 25))
p = np.round(np.linspace(0, SLCnbcols, 25))
L, P = np.meshgrid(l,p)

offset = 720+4096+4680+16384+9860+1620+325000+511000+3072+728000

with open(fileLED,'rb') as file:
    file.seek(offset+1024)
    coeffstr = struct.unpack_from("1000s",file.read(1000))[0].decode('utf-8')
    coeffstr = coeffstr.split()
    coeff = []
    for ci in coeffstr:
            coeff.append(float(ci))

with open(fileLED,'rb') as file:
    file.seek(offset+3064)
    origlat = float(struct.unpack_from("20s",file.read(20))[0].decode('utf-8').split()[0])
    origlon = float(struct.unpack_from("20s",file.read(20))[0].decode('utf-8').split()[0])

with open(fileLED,'rb') as file:
    file.seek(offset+2024)
    origpix = float(struct.unpack_from("20s",file.read(20))[0].decode('utf-8').split()[0])
    origlin = float(struct.unpack_from("20s",file.read(20))[0].decode('utf-8').split()[0])

L = L - origlin
P = P - origpix

LAT = coeff[0] * L**4 * P**4 + \
    coeff[1] * L**3 * P**4 + \
    coeff[2] * L**2 * P**4 + \
    coeff[3] * L**1 * P**4 + \
    coeff[4] * L**0 * P**4 + \
    coeff[5] * L**4 * P**3 + \
    coeff[6] * L**3 * P**3 + \
    coeff[7] * L**2 * P**3 + \
    coeff[8] * L**1 * P**3 + \
    coeff[9] * L**0 * P**3 + \
    coeff[10] * L**4 * P**2 + \
    coeff[11] * L**3 * P**2 + \
    coeff[12] * L**2 * P**2 + \
    coeff[13] * L**1 * P**2 + \
    coeff[14] * L**0 * P**2 + \
    coeff[15] * L**4 * P**1 + \
    coeff[16] * L**3 * P**1 + \
    coeff[17] * L**2 * P**1 + \
    coeff[18] * L**1 * P**1 + \
    coeff[19] * L**0 * P**1 + \
    coeff[20] * L**4 * P**0 + \
    coeff[21] * L**3 * P**0 + \
    coeff[22] * L**2 * P**0 + \
    coeff[23] * L**1 * P**0 + \
    coeff[24] * L**0 * P**0
    
LON = coeff[25] * L**4 * P**4 + \
    coeff[26] * L**3 * P**4 + \
    coeff[27] * L**2 * P**4 + \
    coeff[28] * L**1 * P**4 + \
    coeff[29] * L**0 * P**4 + \
    coeff[30] * L**4 * P**3 + \
    coeff[31] * L**3 * P**3 + \
    coeff[32] * L**2 * P**3 + \
    coeff[33] * L**1 * P**3 + \
    coeff[34] * L**0 * P**3 + \
    coeff[35] * L**4 * P**2 + \
    coeff[36] * L**3 * P**2 + \
    coeff[37] * L**2 * P**2 + \
    coeff[38] * L**1 * P**2 + \
    coeff[39] * L**0 * P**2 + \
    coeff[40] * L**4 * P**1 + \
    coeff[41] * L**3 * P**1 + \
    coeff[42] * L**2 * P**1 + \
    coeff[43] * L**1 * P**1 + \
    coeff[44] * L**0 * P**1 + \
    coeff[45] * L**4 * P**0 + \
    coeff[46] * L**3 * P**0 + \
    coeff[47] * L**2 * P**0 + \
    coeff[48] * L**1 * P**0 + \
    coeff[49] * L**0 * P**0

data_xml['latitude'] = list(LAT.flatten())
data_xml['longitude'] = list(LON.flatten())
data_xml['line'] = list((L + origlin).flatten())
data_xml['pixel'] = list((P + origpix).flatten())
                
# For the times
with open(fileSUM,'r') as fi: 
    for line in fi:
        if 'SceneStartDateTime=' in line: 
            value = line.split('=')[-1].split('\n')[0].replace('"','')
            data_xml['startTime'] = '%s-%s-%sT%s:%s:%s.%06dZ' % (
                            value.split()[0][0:4],
                            value.split()[0][4:6],
                            value.split()[0][6:8],
                            value.split()[1].split(':')[0],
                            value.split()[1].split(':')[1],
                            value.split()[1].split(':')[2].split('.')[0],
                            float(value.split()[1].split(':')[2].split('.')[1])*1000
                                    )
        elif 'SceneCenterDateTime=' in line: 
            value = line.split('=')[-1].split('\n')[0].replace('"','')
            data_xml['centerTime'] = '%s-%s-%sT%s:%s:%s.%06dZ' % (
                            value.split()[0][0:4],
                            value.split()[0][4:6],
                            value.split()[0][6:8],
                            value.split()[1].split(':')[0],
                            value.split()[1].split(':')[1],
                            value.split()[1].split(':')[2].split('.')[0],
                            float(value.split()[1].split(':')[2].split('.')[1])*1000
                            )
        elif 'SceneEndDateTime=' in line: 
            value = line.split('=')[-1].split('\n')[0].replace('"','')
            data_xml['stopTime'] = '%s-%s-%sT%s:%s:%s.%06dZ' % (
                            value.split()[0][0:4],
                            value.split()[0][4:6],
                            value.split()[0][6:8],
                            value.split()[1].split(':')[0],
                            value.split()[1].split(':')[1],
                            value.split()[1].split(':')[2].split('.')[0],
                            float(value.split()[1].split(':')[2].split('.')[1])*1000
                            )

lonpts = data_xml['longitude']
latpts = data_xml['latitude']

pts= [(x,y) for x in lonpts for y in latpts]

pts=np.array([np.array(lonpts), np.array(latpts)]).T
hull = ConvexHull(pts)
a = Polygon(list(zip(pts[hull.vertices,0], pts[hull.vertices,1])))

print(data_xml['startTime'])
print(a)