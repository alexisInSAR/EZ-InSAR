#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

"""**EZInSAR application**: Open an EZ-InSAR container to run EZ-InSAR on non-Linux platforms

Attributes:
    __docstringapp__ (str): doctring string for docopt interpreter

Example:
    The help can be launched by using the following command:: 
        
        $ ezinsar docker -v <str> [options]

Changelog:
    * 3.0.0: Initial version, Dec. 2024

"""

__docstringapp__ =  """EZInSAR application: Open an EZ-InSAR container to run EZ-InSAR on non-Linux platforms

usage: ezinsar docker -v <str> [options]

Arguments:
    -v, --volume <str>             Lists of volumes required to be mounted (the first volume will be defined as work directory)

Optional-arguments:
    -p, --port <str>                Polarisation [default: 8050] 
    
Other-options:
    -h, --help
    -q, --quiet         Suppress verbose

"""

from docopt import docopt
import docker
import os 
import subprocess
from ezinsar import usermessage
from ezinsar import constants
__copyright__ = constants.__copyright__

def main():
    """Main function"""
    args = docopt(__docstringapp__)

    if args['--quiet']: 
        verbose = False
    else:
        verbose = True
    
    cli = docker.from_env()
    listimage = cli.images.list(filters = { "reference" : "ezinsar"})

    usermessage.openingmsg(__name__,__name__,__file__,__copyright__,'EZ-InSAR Dockerisation',None,verbose)
    
    if listimage: 
        ## List the ezinsar containers
        listcont = cli.containers.list(all=True, filters = { "name" : "ezinsar"})
        if listcont:  
            idx = []
            for di in listcont: 
                idx.append(int(di.name.split('ezinsar')[-1]))
            idx = idx[-1] + 1
        else: 
            idx = 0

        usermessage.ezprint('The docker-container name will be ezinsar%s. Please use docker to manage the containers.' % (idx),None,verbose)

        ## Create the command 
        cmd = 'docker run '
        for vi in args['--volume'].split(','): 
            cmd = cmd + '-v %s:/mnt/Data/%s ' % (vi,vi.split(os.sep)[-1])
            
        cmd = cmd + '-w %s --name ezinsar%s -p %s:%s -it ezinsar' % ('/mnt/Data/',idx,args['--port'],args['--port'])
       
        ## Run the container
        process = subprocess.Popen(cmd.split())

        try: 
            process.wait(timeout=3600*365*24) 
        except KeyboardInterrupt:
            process.terminate()
        
    else: 
        raise ValueError(usermessage.errormsg(__name__,__name__,__file__,__copyright__,'No EZ-InSAR image. Please go to the documentation in order to build an EZ-InSAR image for Docker.',None))
    
if __name__=='__main__':
    main()