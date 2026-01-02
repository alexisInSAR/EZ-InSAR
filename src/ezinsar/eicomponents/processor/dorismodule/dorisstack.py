#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to manipulate the Doris stack (ie. network computation)

The module allows to manipuate the stack with Doris processor for EZ-InSAr. 
    
    (From `ezinsar` package)

Changelog:
        * 1.0.0: Initial version, Dec. 2024

Todo: 
        * Optimisation for orbit detection

"""

################################################################################
## Python packages
################################################################################
import os
import numpy as np
from typing import Optional, Union
import jdcal
import datetime
from scipy.spatial import Delaunay
import shutil
import subprocess
import pandas as pd
import matplotlib.pyplot as plt

from ezinsar import usermessage
from ezinsar import constants
from ezinsar.eicomponents.processor.dorismodule import doristools
__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
## computeifgnetwork FUNCTION
################################################################################
def computeifgnetwork(SLCdirectory, 
        datefile,
        refimage,
        modePS: Optional[bool]  = True,
        modeSBAS: Optional[bool] = False,
        bperp_mm: Optional[list] = [-1e6,1e6], 
        delta_T: Optional[list] = [-1e6,1e6], 
        delta_n_max: Optional[int] = 1,
        bperp_th: Optional[int] = 50, 
        pol: Optional[str] ='vv',
        orbit_sampling: Optional[int] = 6,
        verbose: Optional[bool] = True,
        log: Optional[str] = None):
        """Compute an interferometric network using Doris

        The function will compute an interferometric network from Doris. 

        Args:
                SLCdirectory (str): Path of the resampled SLC directory
                datefile (str): date file
                refimage (str): parameter file of the reference image
                modePS (bool, Optional): Enable the single-master network. [Default: `True`]
                modeSBAS (str or bool, Optional): Enable the multi-reference network. Can be `False`, ``lt`` or ``delaunay``. [Default: `False`]
                bperp_mm (list of float, Optional): Thresholds of the perpendicular baselines in metres. [Default: ``[-1e6 1e6]``]
                delta_T (list of float, Optional): Thresholds of the temporal baselines in days. [Default: ``[-1e6 1e6]``]
                delta_n_max (int): Max. connectivity. [Default: ``1``]
                bperp_th (int or float, Optional): Thresholds of the 1-year interferograms, only for lt optimisation. [Default: ``50``]
                pol (str, Optional): Polarisation. [Default: ``vv``]
                orbit_sampling (int, Optional): Temporal sampling, only for lt optimisation. [Default: ``6``]
                verbose (bool, Optional): Verbose mode. [Default: `True`]
                log (str, Optional): Log file. [Default: `None`]

        """
        cur_dir = os.getcwd()

        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,computeifgnetwork.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        if not os.path.isdir(SLCdirectory):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,computeifgnetwork.__name__,__file__,__copyright__,
                        'SLCdirectory','directory',log))
        
        if not os.path.isfile(datefile):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,computeifgnetwork.__name__,__file__,__copyright__,
                        'datefile','file',log))
        
        if not os.path.isfile(refimage):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,computeifgnetwork.__name__,__file__,__copyright__,
                        'refimage','file',log))

        if not isinstance(modePS,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,computeifgnetwork.__name__,__file__,__copyright__,
                        'modePS',"True of False",log))

        if not modeSBAS in [False, 'normal','delaunay','lt']:
                raise TypeError(usermessage.typeerrormsg(
                        __name__,computeifgnetwork.__name__,__file__,__copyright__,
                        'modeSBAS',"'normal','delaunay','lt'",log))
        
        if not pol in ['vv','vh','hv','hh']:
                raise TypeError(usermessage.typeerrormsg(
                        __name__,computeifgnetwork.__name__,__file__,__copyright__,
                        'pol',"'vv','vh','hv','hh'",log))
        
        if not (isinstance(bperp_th,int) or isinstance(bperp_th,float)):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,computeifgnetwork.__name__,__file__,__copyright__,
                        'bperp_th','int or float',log))
        
        if not isinstance(orbit_sampling,int):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,computeifgnetwork.__name__,__file__,__copyright__,
                        'orbit_sampling','int',log))

        usermessage.openingmsg(__name__,computeifgnetwork.__name__,__file__,__copyright__,'Compute an interferometric network for Doris',log,verbose)
        
        ## Given the parameters
        if modePS == True: 
                usermessage.ezprint('Mode Single-Master Network: %s' % (modePS),log,verbose)
                usermessage.ezprint('\tAll parameters will be ignored.',log,verbose)

        if not modeSBAS == False: 
                usermessage.ezprint('Mode Multi-reference Network: %s' % (modeSBAS),log,verbose)

                if modeSBAS == 'normal': 
                        usermessage.ezprint('\tNo optimisation',log,verbose)
                        usermessage.ezprint('\tBperp threshold: %s' % (bperp_mm),log,verbose)
                        usermessage.ezprint('\tBtemp threshold: %s' % (delta_T),log,verbose)
                        usermessage.ezprint('\tMax. connectivity: %s' % (delta_n_max),log,verbose)

                elif modeSBAS == 'delaunay': 
                        usermessage.ezprint('\tOptimisation: Delaunay',log,verbose)
                        usermessage.ezprint('\tAll other parameters will be ignored.',log,verbose)

                elif modeSBAS == 'lt': 
                        usermessage.ezprint('\tOptimisation: Long-term network',log,verbose)
                        usermessage.ezprint('\tBperp threshold (for the long-term ifg(s)): %s' % (bperp_th),log,verbose)
                        usermessage.ezprint('\tAverage temporal sampling: %s' % (orbit_sampling),log,verbose)
                        usermessage.ezprint('\tAll other parameters will be ignored.',log,verbose)

        ## Compute of the super-single network 
        usermessage.ezprint('Computation of the super-single network using Doris: ...',log,verbose)

        if os.path.isdir(SLCdirectory+os.sep+'tmpbase'):
                shutil.rmtree(SLCdirectory+os.sep+'tmpbase')
        os.mkdir(SLCdirectory+os.sep+'tmpbase')
        os.chdir(SLCdirectory+os.sep+'tmpbase')
                
        ## Create the input cards and the job
        if 'rslc' in refimage:
                ext = 'rslc'
        else:
                ext = 'slc'

        refdate = refimage.split(os.sep)[-1].split('.')[0]

        h = 0
        dict_cmd = {}
        with open(datefile) as fi:
                for di in fi:
                        dslc = di.strip()
                        if not dslc == refdate:

                                with open('config_card_%s.tmp' % (h),'w') as fout: 

                                        fout.write('cc **********************************************************************\n')
                                        fout.write('c ***  Doris \inputfile *****\n')
                                        fout.write('c **********************************************************************\n')
                                        fout.write(' c\n')
                                        fout.write(' c\n')
                                        fout.write(' comment  ___general options___\n')
                                        fout.write(' c\n')
                                        fout.write('c SCREEN          debug                           // level of output to standard out\n')
                                        fout.write('SCREEN          info                           // level of output to standard out\n')
                                        fout.write('MEMORY          100                           // MB\n')
                                        fout.write('BEEP            error                            // level of beeping\n')
                                        fout.write('OVERWRITE                                       // overwrite existing files\n')
                                        fout.write('BATCH                                           // non-interactive\n')
                                        fout.write('c LISTINPUT OFF                                 // prevents copy of this file to log\n')
                                        fout.write('c\n')
                                        fout.write('PROCESS          COARSEORB\n')
                                
                                        fout.write('c                                              //\n')
                                        fout.write(' c                                              //\n')
                                        fout.write(' comment  ___the general io files___            //\n')
                                        fout.write(' c                                              //\n')
                                        fout.write('LOGFILE         %s                         // log file\n' % (log))
                                        fout.write('M_RESFILE       %s  // parameter file\n' % (refimage))
                                        fout.write('S_RESFILE       %s                     // parameter file\n' % ('..'+os.sep+dslc+'.'+pol+'.'+ext+'.res'))
                                        fout.write('I_RESFILE       %s               // parameter file\n' % (refdate+'_'+dslc+'.tmpbase'))
                                        fout.write('DUMPBASELINE    50 50\n')
                                        fout.write(' c                                              //\n')
                                        fout.write('STOP\n')
                                
                                dict_cmd['cmd%s' % (h)] = [ ['doris','config_card_%s.tmp' % (h)],
                                        'config_card_%s.tmp' % (h)]
                                        
                                h = h + 1

        ## Run Doris
        doristools.wrappersubprocess(dict_cmd,0,1,False,log)
        for keyi in list(dict_cmd.keys()):
                if os.path.isfile(dict_cmd[keyi][1]):
                        os.remove(dict_cmd[keyi][1])

        ## Read the bperp
        btemp = []
        bperp = []
        dates = []

        with open(datefile) as fi:
                for di in fi:
                        dslc = di.strip()
                        d1 = datetime.datetime.strptime(refdate, '%Y%m%d')
                        d2 = datetime.datetime.strptime(dslc, '%Y%m%d')

                        dates.append(d2)

                        if not dslc == refdate: 
                                val = float(subprocess.check_output('grep "Bperp" '+refdate+'_'+dslc+'.tmpbase'+" | awk 'END {print $3}'", shell=True, encoding="utf-8").strip())
                        else: 
                                val = 0

                        if d1 < d2:
                                usermessage.ezprint('\tMaster: %s / Slave: %s / Bperp: %s [m] / Btemp: %s [days]' % (d1,
                                        d2,val,d2-d1),log,verbose)
                        if d1 > d2:
                                usermessage.ezprint('\tMaster: %s / Slave: %s / Bperp: %s [m] / Btemp: %s [days]' % (d1,
                                        d2,val,d2-d1),log,verbose)

                        btemp.append(d2-d1)
                        bperp.append(val)

        SSMnet = {'Idx': [],
                'Master': [],
                'Slave': [],
                'Bperp': [],
                'DT': []}

        for idx, di in enumerate(bperp):
                SSMnet['Idx'].append(idx)
                SSMnet['Master'].append(datetime.datetime.strptime(refdate, '%Y%m%d'))
                SSMnet['Slave'].append(dates[idx])
                SSMnet['Bperp'].append(bperp[idx])
                SSMnet['DT'].append(btemp[idx])

        h = 0 
        with open('bperp_file_Single.txt','w') as fps: 
                for idx, di in enumerate(SSMnet['Master']): 
                        if not SSMnet['Master'][idx].strftime('%Y%m%d') == SSMnet['Slave'][idx].strftime('%Y%m%d'): 
                                check = 1
                        else: 
                                check = 0
                        fps.write('%d\t%s\t%s\t%10.3f\t%10.3f\t%s\t%10.3f\t%10.3f\t%10.3f\t%10.3f\t%d\n' % 
                                (h, 
                                SSMnet['Master'][idx].strftime('%Y%m%d'),
                                SSMnet['Slave'][idx].strftime('%Y%m%d'),
                                SSMnet['Bperp'][idx],
                                SSMnet['DT'][idx].days,
                                SSMnet['Master'][idx].strftime('%Y%m%d'),
                                0,
                                SSMnet['Bperp'][idx],
                                0,
                                SSMnet['DT'][idx].days,
                                check,
                                ))
                        h = h + 1

        usermessage.ezprint('\tdone',log,verbose)

        # Opne the full network
        usermessage.ezprint('Compute the full network:...',log,verbose)

        fullnet = {'Idx': [],
                'Master': [],
                'Slave': [],
                'Bperp': [],
                'DT': [], 
                'MasterREF': [],
                'MasterBperp': [],
                'SlaveBperp': [],
                'MasterBtemp': [],
                'SlaveBtemp': [],
                }

        h = 0
        for i1 in np.arange(0,len(dates),1):
                for i2 in np.arange(i1+1,len(dates),1):
                        fullnet['Idx'].append(h)
                        fullnet['Master'].append(dates[i1])
                        fullnet['Slave'].append(dates[i2])
                        fullnet['Bperp'].append(bperp[i2]-bperp[i1])
                        fullnet['DT'].append(dates[i2]-dates[i1])
                        fullnet['MasterREF'].append(datetime.datetime.strptime(refdate, '%Y%m%d'))
                        fullnet['MasterBperp'].append(bperp[i1])
                        fullnet['SlaveBperp'].append(bperp[i2])
                        fullnet['MasterBtemp'].append(dates[i1]-datetime.datetime.strptime(refdate, '%Y%m%d'))
                        fullnet['SlaveBtemp'].append(dates[i2]-datetime.datetime.strptime(refdate, '%Y%m%d'))

                        usermessage.ezprint('\tMaster: %s / Slave: %s / Bperp: %s [m] / Btemp: %s [days]' % (dates[i1],
                                        dates[i2],bperp[i2]-bperp[i1],dates[i2]-dates[i1]),None,False)

                        h = h + 1

        usermessage.ezprint('\tdone',log,verbose)


        ## For the normal network
        if modeSBAS == 'normal': 
                usermessage.ezprint('Compute the normal multi-reference network',log,verbose)
                fsbas = open('bperp_file_MR.txt','w')

                h = 0
                for idx, idxifg in enumerate(fullnet['Idx']):
                        if fullnet['DT'][idx].days <= delta_T[1] and fullnet['DT'][idx].days >= delta_T[0]: 
                                if fullnet['Bperp'][idx] <= bperp_mm[1] and fullnet['Bperp'][idx] >= bperp_mm[0]: 
                                        
                                        npos1 = 0
                                        hh = 0
                                        for di in dates:
                                                if fullnet['Master'][idx] == di: 
                                                        npos1 = hh
                                                hh = hh + 1

                                        npos2 = 0
                                        hh = 0
                                        for di in dates:
                                                if fullnet['Slave'][idx] == di: 
                                                        npos2 = hh
                                                hh = hh + 1
                                        
                                        if (npos2 - npos1) <= delta_n_max: 
                                                
                                                usermessage.ezprint('\tMaster: %s / Slave: %s / Bperp: %s [m] / Btemp: %s [days]' % (fullnet['Master'][idx],
                                                        fullnet['Slave'][idx],
                                                        fullnet['Bperp'][idx],
                                                        fullnet['DT'][idx]),log,verbose)

                                                fsbas.write('%d\t%s\t%s\t%10.3f\t%10.3f\t%s\t%10.3f\t%10.3f\t%10.3f\t%10.3f\t%d\n' % 
                                                        (h, 
                                                        fullnet['Master'][idx].strftime('%Y%m%d'),
                                                        fullnet['Slave'][idx].strftime('%Y%m%d'),
                                                        fullnet['Bperp'][idx],
                                                        fullnet['DT'][idx].days, 
                                                        fullnet['MasterREF'][idx].strftime('%Y%m%d'), 
                                                        fullnet['MasterBperp'][idx], 
                                                        fullnet['SlaveBperp'][idx], 
                                                        fullnet['MasterBtemp'][idx].days, 
                                                        fullnet['SlaveBtemp'][idx].days,
                                                        1) 
                                                )
                                                            
                                                h = h + 1

                fsbas.close()

        # For the Delaunay network
        elif not modeSBAS == False: 
                if modeSBAS == 'delaunay': 
                        usermessage.ezprint('Compute the delaunay network',log,verbose)
                        
                        datesdatetime = []
                        datesjj = []
                        bperp = []
                        for idx, di in enumerate(SSMnet['Slave']): 
                                dslci_date = di
                                datesdatetime.append(dslci_date)
                                datesjj.append(int(sum(jdcal.gcal2jd(dslci_date.year, dslci_date.month, dslci_date.day))))
                                bperp.append(SSMnet['Bperp'][idx])
                                        
                        points = np.array([ [x,y] for x,y in zip(datesjj,bperp)])
                        tri = Delaunay(points)

                        ifg = []

                        for trii in tri.simplices: 
                                if trii[0] < trii[1]: 
                                        ifga = (SSMnet['Slave'][trii[0]],SSMnet['Slave'][trii[1]])
                                else:
                                        ifga = (SSMnet['Slave'][trii[1]],SSMnet['Slave'][trii[0]])
                                if trii[1] < trii[2]: 
                                        ifgb = (SSMnet['Slave'][trii[1]],SSMnet['Slave'][trii[2]])
                                else:
                                        ifgb = (SSMnet['Slave'][trii[2]],SSMnet['Slave'][trii[1]])
                                if trii[0] < trii[2]: 
                                        ifgc = (SSMnet['Slave'][trii[0]],SSMnet['Slave'][trii[2]])
                                else:
                                        ifgc = (SSMnet['Slave'][trii[2]],SSMnet['Slave'][trii[0]])

                                if not ifga in ifg: 
                                        ifg.append(ifga)
                                if not ifgb in ifg: 
                                        ifg.append(ifgb)
                                if not ifgc in ifg: 
                                        ifg.append(ifgc)

                ## For the long-term network
                elif modeSBAS == 'lt': 
                        usermessage.ezprint("Compute the 'long-term' network with a bperp th of %f m for the 1-year interferograms" % (bperp_th),log,verbose)
                        
                        datesdatetime = []
                        datesjj = []
                        bperp = []
                        for idx, di in enumerate(SSMnet['Slave']): 
                                dslci_date = di
                                datesdatetime.append(dslci_date)
                                datesjj.append(int(sum(jdcal.gcal2jd(dslci_date.year, dslci_date.month, dslci_date.day))))
                                bperp.append(SSMnet['Bperp'][idx])

                        h = 1
                        stepml = np.arange(len(datesdatetime),0,-1)-1
                        ifg = []

                        for i1 in stepml:
                                #For n-1
                                if i1-1 >= 0:
                                        dm = SSMnet['Slave'][i1-1]
                                        ds = SSMnet['Slave'][i1]
                                        ifg.append((dm,ds))

                                #For n-2
                                if i1-2 >= 0:
                                        dm = SSMnet['Slave'][i1-2]
                                        ds = SSMnet['Slave'][i1]
                                        ifg.append((dm,ds))

                                #For n-3
                                if i1-3 >= 0:
                                        dm = SSMnet['Slave'][i1-3]
                                        ds = SSMnet['Slave'][i1]
                                        ifg.append((dm,ds))

                                #For n-3months
                                ds = datesjj[i1]
                                dsbis = ds - 3*(365.25/12)
                                diff = np.abs(np.array(datesjj) - dsbis)
                                idxmin = np.argmin(diff)
                                if (diff[idxmin] <= orbit_sampling+0.1) and (idxmin != 0):
                                        dm = SSMnet['Slave'][i1]
                                        ds = SSMnet['Slave'][idxmin]
                                        if i1 < idxmin:
                                                ifg.append((dm,ds))
                                        else:
                                                ifg.append((ds,dm))

                                #For n-1year
                                ds = datesjj[i1]
                                dsbis = ds - 12*(365.25/12)
                                diff = np.abs(np.array(datesjj) - dsbis)
                                idxmin = np.argmin(diff)
                                if (diff[idxmin] <= 2.*orbit_sampling+0.1) and (idxmin != 0):
                                        d1 = SSMnet['Slave'][i1]
                                        d2 = SSMnet['Slave'][idxmin]

                                        if i1 < idxmin:
                                                dm = d1
                                                ds = d2
                                        else:
                                                dm = d2 
                                                ds = d1

                                        # Cleaning of duplicate
                                        duplicate = False
                                        tmp = [item for item in ifg if item[0] == dm]
                                        if tmp:
                                                tmpbis = [item[1] for item in tmp]
                                        
                                                dslave = datetime.datetime.strptime(ds, '%Y%m%d')
                                                dslavejj = int(sum(jdcal.gcal2jd(dslave.year, dslave.month, dslave.day)))

                                                dslavejjtest = []
                                                for di in tmpbis:
                                                        dslavetest = datetime.datetime.strptime(ds, '%Y%m%d')
                                                        dslavejjtest.append(int(sum(jdcal.gcal2jd(dslavetest.year, dslavetest.month, dslavetest.day))))

                                                for b in dslavejjtest:
                                                        if np.abs(dslavejj-b)<3*orbit_sampling:
                                                                duplicate = True
                                                
                                        if duplicate == False:
                                                npos = (np.where((np.array(fullnet['Master']) == dm) & (np.array(fullnet['Slave']) == ds)))[0][0]
                                                if abs(float(fullnet['Bperp'][npos])) <= bperp_th:
                                                        ifg.append((dm,ds))

                ifg = sorted(list(dict.fromkeys(ifg)), key=lambda element: (element[0],element[1]))
                fsbas = open('bperp_file_MR.txt','w')
                h = 0 
                for d1,d2 in ifg:
                        npos = np.where((np.array(fullnet['Master']) == d1) & (np.array(fullnet['Slave']) == d2))[0][0]
                        
                        usermessage.ezprint('\tMaster: %s / Slave: %s / Bperp: %s [m] / Btemp: %s [days]' % (fullnet['Master'][npos],
                                fullnet['Slave'][npos],
                                fullnet['Bperp'][npos],
                                fullnet['DT'][npos]),log,verbose)

                        fsbas.write('%d\t%s\t%s\t%10.3f\t%10.3f\t%s\t%10.3f\t%10.3f\t%10.3f\t%10.3f\t%d\n' % 
                                (h, 
                                fullnet['Master'][npos].strftime('%Y%m%d'),
                                fullnet['Slave'][npos].strftime('%Y%m%d'),
                                fullnet['Bperp'][npos],
                                fullnet['DT'][npos].days,
                                fullnet['MasterREF'][npos].strftime('%Y%m%d'), 
                                fullnet['MasterBperp'][npos], 
                                fullnet['SlaveBperp'][npos], 
                                fullnet['MasterBtemp'][npos].days, 
                                fullnet['SlaveBtemp'][npos].days,
                                1))
                        
                        h = h + 1

                fsbas.close()     

        usermessage.ezprint('\tdone',log,verbose)

        # Merge the files                  
        usermessage.ezprint('Merge the file(s) for the processing:...',log,verbose)

        if modePS == True and modeSBAS == False: 
                shutil.copy('bperp_file_Single.txt',SLCdirectory+os.sep+'bperp_file_Single.txt')
                shutil.copy('bperp_file_Single.txt',SLCdirectory+os.sep+'bperp_file.txt')

        elif modePS == False and (not modeSBAS == False): 
                shutil.copy('bperp_file_Single.txt',SLCdirectory+os.sep+'bperp_file_Single.txt')
                shutil.copy('bperp_file_MR.txt',SLCdirectory+os.sep+'bperp_file.txt')
        else:   
                h = 0 
                with open(SLCdirectory+os.sep+'bperp_file.txt','w') as fout: 
                        with open('bperp_file_Single.txt','r') as fi:
                                for li in fi: 
                                        fout.write('%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % 
                                                (h, 
                                                li.split()[1],
                                                li.split()[2],
                                                li.split()[3],
                                                li.split()[4],
                                                li.split()[5],
                                                li.split()[6],
                                                li.split()[7],
                                                li.split()[8],
                                                li.split()[9],
                                                li.split()[10]))
                                        h = h + 1

                        with open('bperp_file_MR.txt','r') as fi:
                                for li in fi: 
                                        fout.write('%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % 
                                                (h, 
                                                li.split()[1],
                                                li.split()[2],
                                                li.split()[3],
                                                li.split()[4],
                                                li.split()[5],
                                                li.split()[6],
                                                li.split()[7],
                                                li.split()[8],
                                                li.split()[9],
                                                li.split()[10]))
                                        h = h + 1

                shutil.copy('bperp_file_MR.txt',SLCdirectory+os.sep+'bperp_file_MR.txt')
                shutil.copy('bperp_file_Single.txt',SLCdirectory+os.sep+'bperp_file_Single.txt')

        usermessage.ezprint('\tdone',log,verbose)

        if os.path.isdir(SLCdirectory+os.sep+'tmpbase'):
                shutil.rmtree(SLCdirectory+os.sep+'tmpbase')

        os.chdir(cur_dir)                               

################################################################################
## baselinefigure FUNCTION
################################################################################
def baselinefigure(file, 
        figure=None, 
        verbose = True,
        log = None):
        """Create an interferometric-network figure for Doris

        The function will create an interferometric-network figure for Doris.

        Args: 
                file (str): Baseline file 
                figure (str): Figure file. If `None`, the figure will be displayed.  
                verbose (bool, Optional): Verbose mode. [Default: `True`]
                log (str, Optional): Log file. [Default: `None`]

        """
        cur_dir = os.getcwd()

        if not isinstance(verbose,bool):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,baselinefigure.__name__,__file__,__copyright__,
                        'verbose','True or False',log))
        
        if not os.path.isfile(file):
                raise TypeError(usermessage.typeerrormsg(
                        __name__,baselinefigure.__name__,__file__,__copyright__,
                        'file','file',log))

        # Plot the network
        usermessage.ezprint('\tPlot the interferometric network from %s ' % (file),log,verbose)

        data = readbaselinefile(file)

        fig = plt.figure()

        for idx, row in data.iterrows():
                plt.plot([datetime.datetime.strptime(row['Master'],'%Y%m%d'),datetime.datetime.strptime(row['Slave'],'%Y%m%d')],
                        [row['Bperp_master'],row['Bperp_slave']],'-k')  
              
        dates = []
        for idx, row in data.iterrows(): 
                dates.append(datetime.datetime.strptime(row['Slave'],'%Y%m%d'))
        plt.scatter(dates, data['Bperp_slave'], c="blue", label="SAR Acquisitions")

        # For the first with multireference network
        plt.scatter(datetime.datetime.strptime(data['Master'][0],'%Y%m%d'), data['Bperp_master'][0], c="blue")
        plt.scatter(datetime.datetime.strptime(data['Ref'][0],'%Y%m%d'), 0, c="red", label="Super-Single Reference Date")

        plt.legend(loc='best')
        plt.title('Network of interferograms. Reference date: %s' %(datetime.datetime.strftime(datetime.datetime.strptime(data['Ref'][0],'%Y%m%d'),'%Y-%m-%d')))
        plt.xlabel("Time")
        plt.ylabel("Perpendicular Baselines [m]")

        if figure == None: 
                figure = file+'.png'
        plt.savefig(figure)

        os.chdir(cur_dir)

        usermessage.ezprint('Please, visualise the network with the figure in: \n\t%s' % (figure),log,verbose)

################################################################################
## readbaselinefile FUNCTION
################################################################################
def readbaselinefile(file):
        """Read a baseline file

        The function will read a Doris baseline file. 

        Args: 
                file (str): Baseline file 

        Returns: 
                dict: Dictionary of baselines

        """
        dtype = {'Idx':int,'Master':str,'Slave':str,'Bperp':float,'Btemp':float,'Ref':str,'Bperp_master':float,'Bperp_slave':float,'Btemp_master':float,'Btemp_slave':float,'check':bool}
        data = pd.read_csv(file,delimiter='\t',names=['Idx','Master','Slave','Bperp','Btemp','Ref','Bperp_master','Bperp_slave','Btemp_master','Btemp_slave','Check'],
                dtype=dtype)
        
        return data