#!/usr/bin/env python
#
# This scripts provides the different methods necessary
# for looking and (or) updating LASER reference values for E3 and E4 cells 
#

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!
exec(open('src/laser/laserGetOpt.py').read(), globals()) 

# Laser Argument class
localArgParser=laserArgs(verbose=True)
# Add local arguments that are specific to this macro
localArgParser.add_local_arg('--low',  action='store',  default=0, arghelp='Low gain run \n')
localArgParser.add_local_arg('--high', action='store',  default=0, arghelp='High gain run \n')
localArgParser.add_local_arg('--iov',  action='store',  default=0, arghelp='IOV \n')
# Get arguments from parser
localArgs=localArgParser.args_from_parser()
lg_REF_run=int(localArgs.low)
lg_REF_run=int(localArgs.high)
iov_run   =int(localArgs.iov)

region = []
for module in range(1,65):
    if module==15:
        region.append('EBA_m%02d_c18_highgain'% (module))
        region.append('EBA_m%02d_c18_lowgain'% (module))
        region.append('EBA_m%02d_c19_highgain'% (module))
        region.append('EBA_m%02d_c19_lowgain'% (module))
    else:        
        region.append('EBA_m%02d_c00_highgain'% (module))
        region.append('EBA_m%02d_c00_lowgain'% (module))
        region.append('EBA_m%02d_c01_highgain'% (module))
        region.append('EBA_m%02d_c01_lowgain'% (module))

    if module==18:
        region.append('EBC_m%02d_c18_highgain'% (module))
        region.append('EBC_m%02d_c18_lowgain'% (module))
        region.append('EBC_m%02d_c19_highgain'% (module))
        region.append('EBC_m%02d_c19_lowgain'% (module))
        
    else:
        region.append('EBC_m%02d_c00_highgain'% (module))
        region.append('EBC_m%02d_c00_lowgain'% (module))
        region.append('EBC_m%02d_c01_highgain'% (module))
        region.append('EBC_m%02d_c01_lowgain'% (module))


processors = []

processors.append( Use(lg_REF_run, runType='Las', region=region) )
processors.append( Use(hg_REF_run, runType='Las', region=region) )

processors.append( ReadLaser(diode_num_lg=12, diode_num_hg=13, verbose=True, doPisa=True) )
processors.append( CleanLaser() )

processors.append( FillBetaHVNom() )
#processors.append( Print(region='LBA_m01_c00_highgain') )
#processors.append( Print(region='EBA_m01_c00_highgain') )

schema = 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2'
if (os.environ.get('TUCS')!=None): # Makes Sacha happy!
    schema = 'sqlite://;schema='+getResultDirectory()+'tileSqlite.db;dbname=CONDBR2'

processors.append( WriteDBNew( folder='/TILE/OFL02/CALIB/CES',
                               input_schema=schema,
                               output_schema=schema,
                               tag='RUN2-HLT-UPD1-01',
                               iov=(iov_run,0),
                               writeHV=True, 
                               HVScale=True) )

Go(processors)


