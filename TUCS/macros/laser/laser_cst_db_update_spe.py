#!/usr/bin/env python

import os,sys
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
run_lg=localArgs.low
run_hg=localArgs.high
iov   =localArgs.iov

LB_threshold = 1.5
EB_threshold = 0.5

if ((run_lg != 0) and (run_hg != 0)):
    runs = [run_lg,run_hg]
elif (run_lg != 0):
    runs = [run_lg]
elif (run_hg != 0):
    runs = [run_hg]
else:
    assert False, "No run specified"

# 
# Based on laser_stab_variations.py
#
# This scripts provides the different methods necessary
# for computing relative variations w.r.t reference values
# and store them to the CondDB (need both low and high gain there)
#



# Create the events to be analyzed, and read the LASER information
# getLast option is used only in case you let us decide which run numbers we should use

processors = []

processors.append( Use(runs,runType='Las') ) # specify one run or two runs (HG/LG)

processors.append( ReadLaser(diode_num_lg=0, diode_num_hg=0) )

processors.append( CleanLaser() )

# Read the reference values from the CondDB
#
# useSqlite=True will read info a local from 'tileSqlite.db' file
# (useful for debugging, but you need to create this file first with laser_stab_references.py)

processors.append( ReadBadChFromCool( schema='OFL',
                                    tag='UPD4',
                                    Fast=True,
                                    storeADCinfo=True ) )

d = ReadCalibFromCool( schema='sqlite://;schema=tileSqlite.db;dbname=CONDBR2',
                     folder='/TILE/OFL02/CALIB/CES',
                     runType = 'Las_REF',
                     tag = 'RUN2-HLT-UPD1-01',
                     verbose=False)

## dLBC28 = ReadCalFromCool( schema='sqlite://;schema=/afs/cern.ch/user/t/tilelas/workspace/sv_DB/tileSqlite_ref202705_forLBC28_fvar.db;dbname=CONDBR2',
##                      folder='/TILE/OFL02/CALIB/CES',
##                      runType = 'Las_REF',
##                      tag = 'RUN2-HLT-UPD1-01',
##                      verbose=False)

## dEBC01 = ReadCalFromCool( schema='sqlite://;schema=/afs/cern.ch/user/t/tilelas/workspace/sv_DB/tileSqlite_ref201072_forEBC01_fvar.db;dbname=CONDBR2',
##                      folder='/TILE/OFL02/CALIB/CES',
##                      runType = 'Las_REF',
##                      tag = 'RUN2-HLT-UPD1-01',
##                      verbose=False)

## dLBA13 = ReadCalFromCool( schema='sqlite://;schema=/afs/cern.ch/user/t/tilelas/workspace/sv_DB/tileSqlite_ref215036_forLBA13.db;dbname=CONDBR2',
##                      folder='/TILE/OFL02/CALIB/CES',
##                      runType = 'Las_REF',
##                      tag = 'RUN2-HLT-UPD1-01',
##                      verbose=False)

## dLBA54 = ReadCalFromCool( schema='sqlite://;schema=/afs/cern.ch/user/t/tilelas/workspace/sv_DB/tileSqlite_ref210233_forLBA54.db;dbname=CONDBR2',
##                      folder='/TILE/OFL02/CALIB/CES',
##                      runType = 'Las_REF',
##                      tag = 'RUN2-HLT-UPD1-01',
##                      verbose=False)

dE3E4 = ReadCalibFromCool( schema='sqlite://;schema=tileSqlite.db;dbname=CONDBR2',
                     folder='/TILE/OFL02/CALIB/CES',
                     runType = 'Las_REF',
                     tag = 'RUN2-HLT-UPD1-01',
                     verbose=False)

## d0 = ReadCalFromCool(schema='COOLOFL_TILE/CONDBR2',
##                     runType = 'Las_REF',
##                     folder='/TILE/OFL02/CALIB/CES',
##                     tag = 'UPD4')


## print '  --- Reading LBC28 dedicated reference'


## processors.append(dLBC28)
## # Compute the fiber partitions variations, (stored in event.data['fiber_var'])
## processors.append( getFiberShifts(UseStableCells=True,SkipEmergency=False) ) #We need emergency module LBC28
## processors.append ( StoreFiberShift(RestoreRegion='LBC_m28',verbose=False) ) ## We save the fiber + global variation for LBC28



## print '  --- Reading LBA13 dedicated reference'

## processors.append(dLBA13)
## processors.append( getFiberShifts(UseStableCells=True,SkipEmergency=False) ) #We need emergency module LBA13
## processors.append ( StoreFiberShift(RestoreRegion='LBA_m13') ) ## We save the fiber + global variation for LBA13



## print '  --- Reading LBA54 dedicated reference'

## processors.append(dLBA54)
## processors.append( getFiberShifts(UseStableCells=True,SkipEmergency=False) ) #We need emergency module LBA54
## processors.append ( StoreFiberShift(RestoreRegion='LBA_m54') ) ## We save the fiber + global variation for LBA54


print '  --- Reading E3E4 dedicated reference'

processors.append(dE3E4)
processors.append( getFiberShifts(UseStableCells=True,SkipEmergency=False) ) #We need emergency module E3E4
processors.append ( StoreFiberShift(RestoreRegion='layer_E') ) ## We save the fiber + global variation for E3E4 (E1E2 computed but not stored)


## print '  --- Reading EBC01 dedicated reference'

## processors.append(dEBC01)
## processors.append( getFiberShifts(UseStableCells=True,SkipEmergency=False,verbose=False) ) #We need emergency module EBC01
## processors.append ( StoreFiberShift(RestoreRegion='EBC_m01') ) ## We save the fiber + global variation for EBC01

## #processors.append ( StoreFiberShift(iFiber=5) ) ## We can also save a fiber (ex. #5)


print '  --- Reading latest reference for normal channels'

##processors.append (d) #Reading latest reference for normal calibration


processors.append(d)

processors.append( getFiberShifts(UseStableCells=True,verbose=True) )

## processors.append ( StoreFiberShift(RestoreRegion='LBC_m28',Restore=True,verbose=True) ) ## We  restore fiber shift for LBC28
## processors.append ( StoreFiberShift(RestoreRegion='EBC_m01',Restore=True,verbose=True) ) ## We  restore fiber shift for EBC01
## processors.append ( StoreFiberShift(RestoreRegion='LBA_m54',Restore=True,verbose=True) ) ## We  restore fiber shift for LBA54
## processors.append ( StoreFiberShift(RestoreRegion='LBA_m13',Restore=True,verbose=True) ) ## We  restore fiber shift for LBA13
processors.append ( StoreFiberShift(RestoreRegion='layer_E',Restore=True,verbose=True) ) ## We  restore fiber shift for E layers

processors.append( getPMTShiftsObsolete(Threshold_LB=1.5,Threshold_EB=2.0) ) # 1.5 percent for LB, 2 percent for EB

# CondDB update
e = equalizeHGLG()
e = equalizeHGLG()

processors.append( e )
processors.append( e )



processors.append( WriteDB(runType = 'Las', offline_tag = 'RUN2-HLT-UPD1-00',version=2,runNumber=iov) ) #default is 'RUN2-HLT-UPD1-00', 'RUN2-sUPD4-02'


Go(processors)



