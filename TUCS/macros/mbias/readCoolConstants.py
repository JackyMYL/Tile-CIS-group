#!/usr/bin/env python
# Author: Cora Fischer
#
# access information from COOL database for integrator
#

import os, sys
os.chdir(os.getenv('TUCS','.'))
exec(open('src/mbias/getDatesForCool.py').read(), globals())# give dates or runnumbers, and specified detector regions
exec(open('src/load.py').read(), globals()) # don't remove this!

processors = []

# the user can specifiy partition and also single PMTs data
# if partition=5 or left away it means: use all detector (module and pmt not specified or module=64 and pmt=48!)
# if partition, module and pmt specified: print out of gains, pedestal, rms
# executed via: python macros/readConstants.py --date="xxx" --enddate="xx" --part=x --modu=x --channel=x
# if no options given: the worker will use the latest run and all detector

print part, modu, channel, gain
if (modu!=64 and channel==48 and part!=5) or (modu==64 and channel!=48 and part!=5):
    print "you must specify module and pmt at the same time!"
    sys.exit(2)
if (part==5 and modu!=64 and channel!=48):
    print "you forgot to also specify a partition!"
    sys.exit(2)	
if (part==5 and modu!=64 and channel==48):
    print "you must also specify a channel and a partition!"
    sys.exit(2)
if (part==5 and modu==64 and channel!=48):
    print "you must also specify a module and a partiton!"
    sys.exit(2)
    
if gain not in [0,1,2,3,4,5]:
   print "gain must be in range 0-5!"
   sys.exit(2) 
    
    
print runs #test
#processors.append(Use(run=runs, region=selected_region, runType=run_type))
for i in range(len(runs)):
    processors.append( ReadCool( runType='integrator',
                                    schema='COOLONL_TILE/CONDBR2',
                                    folder='/TILE/ONL01/INTEGRATOR',
                                    partition=part,
                                    module=modu,
                                    pmt=channel,
				    Gain=gain,
				    #runNumber=149659,
				    #runNumber=148890,
                                    #runNumber=129857, 
                                    #runNumber=115551,
                                    #runNumber=101413,
                                    #runNumber=101410,
                                    runNumber=runs[i],
                                    verbose = False) )
    				    
Go(processors)
