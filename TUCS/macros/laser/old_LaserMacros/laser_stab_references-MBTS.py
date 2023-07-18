#!/usr/bin/env python
#
# This scripts provides the different methods necessary
# for looking and (or) updating LASER reference values
#
# SV (viret@in2p3.fr) : 16/07/09 (creation) // 24/09/09 (final revision)
#
# For more info, have a look at the LASER webpage:
#
# http://atlas-tile-laser.web.cern.ch

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#
# !!! CAUTION !!!
#
# Reference values update should be done only by experts
#
# In doubt, please contact the LASER expert (tilelas@mail.cern.ch)
#
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#
# There are two sets of reference values for low gain and for high gain
#
# Low  gain runs needs to be filter 6 / intensity 23000
# High gain runs needs to be filter 8 / intensity 23000
#
# List of



# Create the events to be analyzed, and read the LASER information
# Default value for diode is 0, use 3 for low gain runs, and 1 for high gain runs
# This is automatically set in ReadLaser()
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
hg_REF_run=int(localArgs.high)
iov_run   =int(localArgs.iov)


region=[]

sides = ["EBA", "EBC"]
inner_mbts_modules = [39,40,41,42, 55,56,57,58]
outer_mbts_modules = [[3, 8, 20, 24, 43, 46, 54, 59],
                      [3, 8, 19, 24, 43, 46, 54, 59]]


#inner MBTS
for side in range(2):
    for module in range(8):
        for gain in ["low", "high"]:
            inner_mbts_region = ("%s_m%02d_c04_%sgain") % (sides[side],inner_mbts_modules[module],gain)
            region.append(inner_mbts_region)
# Outer MBTS
for side in range(2):
    for module in range(8):
        for gain in ["low", "high"]:
            outer_mbts_region = ("%s_m%02d_c12_%sgain") % (sides[side],outer_mbts_modules[side][module],gain)
            region.append(outer_mbts_region)

processors = []



processors.append( Use(lg_REF_run, runType='Las', region=region) )
processors.append( Use(hg_REF_run, runType='Las', region=region) )

processors.append( ReadLaser(diode_num_lg=12, diode_num_hg=13, verbose=True, doPisa=True) )
processors.append( CleanLaser() )

#processors.append( WriteDB(runType='Las_REF', offline_tag='RUN2-HLT-UPD1-01', version=2, runNumber=iov_run) )

schema = 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2'
if (os.environ.get('TUCS')!=None): # Makes Sacha happy!
    schema = 'sqlite://;schema='+getResultDirectory()+'tileSqlite.db;dbname=CONDBR2'

processors.append( WriteDBNew( folder='/TILE/OFL02/CALIB/CES',
                               input_schema=schema,
                               output_schema=schema,
                               tag='RUN2-HLT-UPD1-01',
                               iov=(iov_run,0),
                               writeHV=True,
                               setMBTShvZero=False) )

Go(processors)


