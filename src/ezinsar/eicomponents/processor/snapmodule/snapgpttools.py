#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""
Module to add some functions for the SNAP GPT wrapper

The module allows to add some sub-functions for the SNAP GPT wrapper.
    
    (From `ezinsar` package)

Changelog:
        * 1.0.0: Initial version, Dec. 2024

"""

################################################################################
## Python packages
################################################################################
import os 
import subprocess
import random
import string 
from ezinsar import usermessage
from ezinsar import constants
__copyright__ = constants.__copyright__
"""str: Copyright of EZ-InSAR
"""

################################################################################
################################################################################
class snapgpt:

  ################################################################################
  ## Initialistion of the class
  ################################################################################
  def __init__(self,
    cachesize = '1024.0 MB',
    nbthread = 4,
    cleancache = True, 
    debugmode = True,
    ):
          
    self.path = constants.__requirement_SNAP_GPT__
    self.version = None
    self.command = None 
    self.cachesize = cachesize
    self.nbthread = nbthread
    self.cleancache = cleancache
    self.debugmode = debugmode
    self.xmltxt = ''
    self.pathxml = None
    self.listoperator = []

    # pr = subprocess.Popen(['%s%s%s' % (self.path,os.sep,'gpt'),'--diag'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # self.version = pr.stdout.readlines()[0].strip()
    self.version = 'SNAP Version XX.0'

  ################################################################################
  ## Method to print the attributes
  ################################################################################
  def print(self):
    """Print the class attributes"""

    attrs = vars(self)
    print(', '.join("%s: %s" % item for item in attrs.items()))

    return self

  ################################################################################
  ## Add the initiale part of the xml file
  ################################################################################
  def xmlinit(self): 
    """"Initiliase the xml file"""

    self.xmltxt = """
<graph id="Graph">
\t<version>1.0</version>
""" 
    return self
    
  ################################################################################
  ## Terminate the the xml file
  ################################################################################
  def xmlclose(self): 
    """"Terminate the xml file"""

    self.xmltxt = self.xmltxt+"""</graph>"""
    
    return self
  
  ################################################################################
  ## Operator
  ################################################################################
  def ProductSetReader(self,listfile): 

    self.xmltxt = self.xmltxt + """\t<node id="ProductSet-Reader">
\t\t<operator>ProductSet-Reader</operator>
\t\t<parameters class="com.bc.ceres.binding.dom.XppDomElement">
\t\t\t<fileList>%s</fileList>
\t\t</parameters>
\t</node>
""" % (','.join(listfile))
    
    self.listoperator.append('ProductSet-Reader')
    
    return self
  
  def SliceAssembly(self,polarisationlist): 

    self.xmltxt = self.xmltxt + """\t<node id="SliceAssembly">
\t\t<operator>SliceAssembly</operator>
\t\t<sources>
\t\t\t<sourceProduct.2 refid="%s"/>
\t\t</sources>
\t\t<parameters class="com.bc.ceres.binding.dom.XppDomElement">
\t\t<selectedPolarisations>%s</selectedPolarisations>
\t\t</parameters>
\t</node>
""" % (self.listoperator[-1],','.join(polarisationlist).upper())
    
    self.listoperator.append('SliceAssembly')
    
    return self
  
  def SliceAssembly2(self,polarisationlist): 

    self.xmltxt = self.xmltxt + """\t<node id="SliceAssembly">
\t\t<operator>SliceAssembly</operator>
\t\t<sources>
""" 
    for idx, li in enumerate(self.listoperator): 
      self.xmltxt = self.xmltxt + """\t\t\t<sourceProduct.%s refid="%s"/>
""" % (idx+1,li)
    self.xmltxt = self.xmltxt + """\t\t</sources>
\t\t<parameters class="com.bc.ceres.binding.dom.XppDomElement">
\t\t<selectedPolarisations>%s</selectedPolarisations>
\t\t</parameters>
\t</node>
""" % (','.join(polarisationlist).upper())
    
    self.listoperator.append('SliceAssembly')
    
    return self
  
  def TOPSARSplit(self,IW,minIDXburst,maxDXburst): 

    self.xmltxt = self.xmltxt + """\t<node id="TOPSAR-Split">
\t\t<operator>TOPSAR-Split</operator>
\t\t<sources>
\t\t\t<sourceProduct refid="%s"/>
\t\t</sources>
\t\t<parameters class="com.bc.ceres.binding.dom.XppDomElement">
\t\t\t<subswath>IW%s</subswath>
\t\t\t<firstBurstIndex>%s</firstBurstIndex>
\t\t\t<lastBurstIndex>%s</lastBurstIndex>
\t\t</parameters>
\t</node>
""" % (self.listoperator[-1],IW,minIDXburst,maxDXburst)
    
    self.listoperator.append('TOPSAR-Split')

  def TOPSARMerge(self): 

    self.xmltxt = self.xmltxt + """\t<node id="TOPSAR-Merge">
\t\t<operator>TOPSAR-Merge</operator>
\t\t<sources>
"""

    if 'Read' in self.listoperator:
      self.xmltxt = self.xmltxt + """\t\t\t<sourceProduct refid="Read"/>
"""
    if 'Read(2)' in self.listoperator:
      self.xmltxt = self.xmltxt + """\t\t\t<sourceProduct.1 refid="Read(2)"/>
"""
    if 'Read(3)' in self.listoperator:
      self.xmltxt = self.xmltxt + """\t\t\t<sourceProduct.2 refid="Read(3)"/>
"""

    self.xmltxt = self.xmltxt + """\t\t</sources>
\t\t<parameters>
\t\t\t<selectedPolarisations/>
\t\t</parameters>
\t</node>
"""

    self.listoperator.append('TOPSAR-Merge')

    return self
  
  def StampsExport(self,targetFolder,psiFormat): 

    self.xmltxt = self.xmltxt + """\t<node id="StampsExport">
\t\t<operator>StampsExport</operator>
\t\t<sources>
"""

    if 'Read' in self.listoperator:
      self.xmltxt = self.xmltxt + """\t\t\t<sourceProduct refid="Read"/>
"""
    if 'Read(2)' in self.listoperator:
      self.xmltxt = self.xmltxt + """\t\t\t<sourceProduct.1 refid="Read(2)"/>
"""

    self.xmltxt = self.xmltxt + """\t\t</sources>
\t\t<parameters>
\t\t\t<targetFolder>%s</targetFolder>
\t\t\t<psiFormat>%s</psiFormat>
\t\t</parameters>
\t</node>
""" % (targetFolder,psiFormat)

    self.listoperator.append('StampsExport')

    return self
  
  def SnaphuImport(self): 

    self.xmltxt = self.xmltxt + """\t<node id="SnaphuImport">
\t\t<operator>SnaphuImport</operator>
\t\t<sources>
"""

    if 'Read' in self.listoperator:
      self.xmltxt = self.xmltxt + """\t\t\t<sourceProduct refid="Read"/>
"""
    if 'Read(2)' in self.listoperator:
      self.xmltxt = self.xmltxt + """\t\t\t<sourceProduct.1 refid="Read(2)"/>
"""
    self.xmltxt = self.xmltxt + """\t\t</sources>
\t\t<parameters>
\t\t</parameters>
\t</node>
"""

    self.listoperator.append('SnaphuImport')

    return self
  
  def ApplyOrbitFile(self): 

    self.xmltxt = self.xmltxt + """\t<node id="Apply-Orbit-File">
\t\t<operator>Apply-Orbit-File</operator>
\t\t<sources>
\t\t\t<sourceProduct refid="%s"/>
\t\t</sources>
\t\t<parameters class="com.bc.ceres.binding.dom.XppDomElement">
\t\t\t<orbitType>Sentinel Precise (Auto Download)</orbitType>
\t\t\t<polyDegree>3</polyDegree>
\t\t\t<continueOnFail>false</continueOnFail>
\t\t</parameters>
\t</node>
""" % (self.listoperator[-1])
    
    self.listoperator.append('Apply-Orbit-File')
    
    return self

  def Read(self,file, idx = 1, sourceBands=None): 

    if idx == 1:
      self.xmltxt = self.xmltxt + """\t<node id="Read">
"""
    else:
      self.xmltxt = self.xmltxt + """\t<node id="Read(%s)">
""" % (idx)

    self.xmltxt = self.xmltxt +"""\t\t<operator>Read</operator>
\t\t<parameters class="com.bc.ceres.binding.dom.XppDomElement">
\t\t\t<file>%s</file>
""" % (file)

    if not sourceBands == None:
      self.xmltxt = self.xmltxt +"""\t\t\t<sourceBands>%s</sourceBands>
""" % (sourceBands)

    self.xmltxt = self.xmltxt +"""\t\t</parameters>
\t</node>
"""
  
    if idx ==1:
      self.listoperator.append('Read')
    else:
      self.listoperator.append('Read(%s)' % (idx))
    
    return self

  def Write(self,file): 

    self.xmltxt = self.xmltxt + """\t<node id="Write">
\t\t<operator>Write</operator>
\t\t<sources>
\t\t\t<sourceProduct refid="%s"/>
\t\t</sources>
\t\t<parameters class="com.bc.ceres.binding.dom.XppDomElement">
\t\t\t<file>%s</file>
\t\t\t<formatName>BEAM-DIMAP</formatName>
\t\t</parameters>
\t</node>
""" % (self.listoperator[-1],file)
    
    self.listoperator.append('Write')
    
    return self
  
  def InSAROverview(self,file): 

    self.xmltxt = self.xmltxt + """\t<node id="InSAR-Overview">
\t\t<operator>InSAR-Overview</operator>
\t\t<sources>
\t\t\t<sourceProduct refid="%s"/>
\t\t</sources>
\t\t<parameters>
\t\t\t<overviewJSONFile>%s</overviewJSONFile>
\t\t</parameters>
\t</node>
""" % (self.listoperator[-1],file)
    
    self.listoperator.append('InSAR-Overview')
    
    return self

  def generic(self,operator,paradic): 

    self.xmltxt = self.xmltxt + """\t<node id="%s">
\t\t<operator>%s</operator>
\t\t<sources>
\t\t\t<sourceProduct refid="%s"/>
\t\t</sources>
\t\t<parameters>
""" % (operator,operator,self.listoperator[-1])

    for ki in paradic.keys():
      self.xmltxt = self.xmltxt + """\t\t\t<%s>%s</%s>
""" % (ki,paradic[ki],ki)

    self.xmltxt = self.xmltxt + """ \t\t</parameters>
\t</node>
""" 
    self.listoperator.append(operator)
    
    return self

  ################################################################################
  ## Run a subprocess for GPT 
  ################################################################################
  def run(self,verbose=True,log=None):
    """Run a subprocess for SNAP

    The function will run a subprocess for SNAP

    """
    usermessage.ezprint('Run SNAP with GPT (%s):' % (self.version),log,verbose)

    ## Create the xml file in-place
    self.pathxml = constants.__cachedir__+os.sep+'gptinput_'+''.join(random.choice(string.ascii_lowercase) for i in range(5)) + '.xml'
    with open(self.pathxml,'w') as fi: 
      fi.write('%s' % (self.xmltxt))

    ## Create the command 
    cmd = [ '%s%sgpt' % (constants.__requirement_SNAP_GPT__,os.sep), 
           '%s' % (self.pathxml)]
    
    if self.debugmode: 
      cmd.append('-e')

    cmd = cmd +['-c','%sM' % (self.cachesize)]
    cmd = cmd +['-q','%s' % (self.nbthread)]

    if self.cleancache: 
      cmd.append('-x')

    usermessage.ezprint('\tCommand: %s' % (' '.join(cmd)),log,verbose)

    ## Display the input parameters
    usermessage.ezprint('\tXML card',log,verbose)
    usermessage.ezprint('%s' % (self.xmltxt),log,verbose)

    ## Run the processing
    usermessage.ezprint('\tRun the processing',log,verbose)

    try: 
      # pr = subprocess.run(cmd)
      os.system(' '.join(cmd))
 
    # try: 
    #   while (line := pr.stdout.readline().strip()) != "":
    #     usermessage.ezprint(line.replace('\n',' '),log,verbose)     
    #   if (not pr.stderr.readline().strip() == ''):
    #     while (line := pr.stderr.readline().strip()) != "":
    #       usermessage.ezprint(line.replace('\n',' '),log,verbose)  
    #     #     raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'Error in the SNAP-GPT processing',log))
          
    except KeyboardInterrupt:
      # pr.terminate()
      raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'Error in the SNAP-GPT processing: user terminated',log))
    
    except:
      # pr.terminate()
      raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'Error in the SNAP-GPT processing: user terminated',log))
    
    usermessage.ezprint('\tdone',log,verbose)

  ################################################################################
  ## Clean method 
  ################################################################################
  def clean(self):
    if not self.pathxml == None:
      if os.path.isfile(self.pathxml):
        os.remove(self.pathxml)

    self.xmltxt = ''
    self.listoperator = []


  
