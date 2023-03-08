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
localArgParser.add_local_arg('--iov', action='store',  default=0, arghelp='IOV \n')
# Get arguments from parser 
localArgs=localArgParser.args_from_parser()
iov_run=int(localArgs.iov)

start_date = date
end_date = enddate

#print ("Using region: ",region)
if region=="MBTS":
    region = ''
    for part in ["EBA","EBC"]: 
        for mod in ["39","40","41","42","55","56","57","58"]: # E6 inner
            region = region + part + "_m" + mod + "_c04,"
        for mod in ["08", "24", "43", "54"]: # E5 outer
                    region = region + part + "_m" + mod + "_c12,"
    region = region[:len(region)-1]
#print(region)
        
processors = []

if isinstance(region,str):
    print (type(region))
#    processors.append( Use(run= start_date,run2= end_date, filter= '6', TWOInput=True, runType='Las', region=region) )
    processors.append( Use(run= start_date,run2= end_date, filter='8',  TWOInput=True, runType='Las', region=region) )
else:
#    processors.append( Use(run= start_date,run2= end_date, filter= '6', TWOInput=True, runType='Las') )
    processors.append( Use(run= start_date,run2= end_date, filter='8',  TWOInput=True, runType='Las') )


if os.path.exists('/data/ntuples/las'):
    b = ReadLaser(processingDir='/data/ntuples/las',
                  diode_num_lg=12, 
                  diode_num_hg=13, 
                  doPisa=True) #, verbose=True
else:
    b = ReadLaser(diode_num_lg=12, diode_num_hg=13, doPisa=True)

processors.append(b)
    
processors.append( CleanLaser() )

processors.append( DoAverageValues(key='gain_Pisa') )

schema = 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2'
if (os.environ.get('TUCS')!=None): 
    schema = 'sqlite://;schema='+getResultDirectory()+'tileSqlite.db;dbname=CONDBR2'

processors.append( WriteDBNew( folder='/TILE/OFL02/CALIB/CES',
                               input_schema=schema,
                               output_schema=schema,
                               tag='RUN2-HLT-UPD1-01',
                               iov=(iov_run,0),
                               writeHV=True, 
                               average_ref=True) )

Go(processors)


