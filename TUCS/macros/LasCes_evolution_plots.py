#!/usr/bin/env python
# Auther :Ammara and Henric 
# date: 1st Nov, 2017
#
# Even though its not FORTRAN, its good to be able to print....
#        1         2         3         4         5         6         7         
############################################################################

import os, sys
os.chdir(os.getenv('TUCS','.'))
exec(open('src/laser/laserGetOpt.py').read(), globals())
exec(open('src/load.py').read(), globals()) # don't remove this!

processors = []

doDirect=False
doGlobal=True

if doGlobal:
    usePisa=True
    filt_pos=8

# Definition of all the LASER runs that need to be used for the study
processors.append( Use(runs, run2=enddate, filter=filt_pos, runType='Las',
                       region=region, TWOInput=twoinput, amp='15000') )

# Read Information from the laser
if os.path.exists('/data/ntuples/las'):

    b = ReadLaser(processingDir='/data/ntuples/las',
                  diode_num_lg=12, 
                  diode_num_hg=13, 
                  doPisa=usePisa) #, verbose=True
else:
    b = ReadLaser(diode_num_lg=12, diode_num_hg=13, doPisa=usePisa)
processors.append( b )
processors.append( CleanLaser() )

# Read Information Of bad channels from COOL DATABASE
processors.append( ReadBchFromCool( schema='COOLOFL_TILE/CONDBR2',
                                    folder='/TILE/OFL02/STATUS/ADC',
                                    tag='UPD4',
                                    Fast=True,
                                    storeADCinfo=True) )

# Definition of all CESIUM the runs that need to be used for the study
processors.append( Use(run=date, run2=enddate, runType='cesium', region=region,
                       cscomment='', keepOnlyActive=True, TWOInput=twoinput,
                       allowC10Errors = True) )

# Read Information from the cesium
processors.append( ReadCsFile(normalize=True, skipITC=True, verbose=True) )


processors.append(ReadCalFromCool(runType='integrator',
                                    schema='COOLOFL_TILE/CONDBR2', 
                                    folder='/TILE/OFL02/INTEGRATOR',
                                    tag= 'RUN2-HLT-UPD1-00',
                                    verbose = False))


processors.append( ReadCalFromCool( runType = 'cesium',
                                    schema = 'COOLOFL_TILE/CONDBR2',
                                    #schema = 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2',
                                    folder = '/TILE/OFL02/CALIB/CES',
                                    tag = 'UPD4',
                                    verbose = False) )


#processors.append( FillBetaHVNom() )

#'''Read the reference values from the Conditions DB'''

schema='sqlite://;schema=/afs/cern.ch/user/k/klimek/public/Laser/Reference/Reference_2018/tileSqlite_February2018_v2.db;dbname=CONDBR2' ##latest version 2018 for combined method
tag='TileOfl02CalibCes-RUN2-UPD4-20'  # tag = 'TileOfl02CalibCes-RUN2-UPD4-18'

if not os.path.isfile("tileSqlite.db"): 
    if os.path.isfile(getResultDirectory()+"tileSqlite.db"): # Makes Sacha happy!
        schema='sqlite://;schema='+getResultDirectory()+'tileSqlite.db;dbname=CONDBR2'
    else:
        schema='COOLOFL_TILE/CONDBR2'

processors.append( ReadCalFromCool( schema=schema,
                                    folder='/TILE/OFL02/CALIB/CES',
                                    runType = 'Las_REF',
                                    tag=tag,
                                    verbose=True) )


#''' Workers that perform the data analysis'''
if doDirect:
  #  ''' Global Correction'''
    processors.append( getGlobalShiftsDirect(siglim=2.0, n_iter=3, verbose=True) )
 #  ''' Fibre correction '''
    processors.append( getFiberShiftsDirect(siglim=1.5, n_iter=3, verbose=True) ) 
# '''  And finally the globally corrected PMT shifts, (stored in event.data['deviation']) '''
    processors.append( getPMTShiftsDirect() )
   # processors.append(compute_EBScale())
    processors.append( scaleEB() ) 

elif doGlobal:
    processors.append( getGlobalShiftsCombined(siglim=2.0, n_iter=3, verbose=True) )
  #   ''' Fiber correction'''
    processors.append(getFiberShiftsCombined(siglim=2.0, n_iter=3, verbose=True) )
 #   ''' And finally the globally corrected PMT shifts, (stored in event.data['deviation'])'''
    processors.append( getPMTShiftsDirect(usePisa=False) )


#'''Plots average response of all PMTs of a given cell type as a function of time'''

processors.append(do_LasCesCell_plots(cells=['A10','A12','A14'], doPdfEps=False, label=''))

#''' Plots Layer averages over time '''
processors.append(do_LasCesLayer_plots(layers=['A', 'BC','D','B'], doPdfEps=False, label=''))


Go( processors )
