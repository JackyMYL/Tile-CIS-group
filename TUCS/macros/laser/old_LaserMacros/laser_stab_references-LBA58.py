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
lg_REF_run=localArgs.low
hg_REF_run=localArgs.high
iov_run   =localArgs.iov

region=['LBA_m58','LBC_m58']

processors = []

if region != '':
    processors.append( Use(lg_REF_run, runType='Las', region=region) )
    processors.append( Use(hg_REF_run, runType='Las', region=region) )
else:
    processors.append( Use(lg_REF_run, runType='Las') )
    processors.append( Use(hg_REF_run, runType='Las') )

processors.append( ReadLaser(diode_num_lg=12, diode_num_hg=13, verbose=True, doPisa=True) )
processors.append( CleanLaser() )

#processors.append( WriteDB(runType='Las_REF', offline_tag='RUN2-HLT-UPD1-01', version=2, runNumber=iov_run) )

schema = 'sqlite://;schema=tileSqlite_March6_Reprocessing_v3.db;dbname=CONDBR2'
if (os.environ.get('TUCS')!=None): # Makes Sacha happy!
    schema = 'sqlite://;schema='+getResultDirectory()+'tileSqlite.db;dbname=CONDBR2'

processors.append( WriteDBNew( folder='/TILE/OFL02/CALIB/CES',
                               input_schema=schema,
                               output_schema=schema,
                               tag='TileOfl02CalibCes-RUN2-UPD4-18',
                               iov=(iov_run,0),
                               writeHV=True) )

Go(processors)


