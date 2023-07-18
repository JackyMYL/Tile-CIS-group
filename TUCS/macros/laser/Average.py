#!/usr/bin/env python
# Atuh: Henric
# date: just after lunch in march 2013
#
# Even though its not FORTRAN, its good to be able to print....
#        1         2         3         4         5         6         7         8
#2345678901234567890123456789012345678901234567890123456789012345678901234567890

import os, sys
os.chdir(os.getenv('TUCS','.'))
exec(open('src/laser/laserGetOpt.py').read(), globals())  # Here I do all the global options parsing
exec(open('src/load.py').read(), globals()) # don't remove this!

processors = []

# Laser Argument class
localArgParser=laserArgs(verbose=True)
# Add local arguments that are specific to this macro
localArgParser.add_local_arg('--newArg', action='store_true',  default=False, arghelp='New argument \n')
# Get arguments from parser
localArgs=localArgParser.args_from_parser()
newArg=localArgs.newArg

runs = date

processors.append( Use(runs, run2=enddate, filter=filt_pos, runType='Las',
                       region=region, TWOInput=twoinput) )

#processors.append( ReadBchFromCool( schema='OFL',
#                                    tag='UPD4',
#                                    Fast=True,
#                                    storeADCinfo=True) )

if os.path.exists('/data/ntuples/las'):
    processors.append( ReadLaser(processingDir='/data/ntuples/las',
                                 diode_num_lg=12, diode_num_hg=13,
                                 verbose=False, doPisa=usePisa) )
else:
    processors.append( ReadLaser(diode_num_lg=12, diode_num_hg=13, verbose=False, doPisa=usePisa ) )

processors.append( CleanLaser() )

#if os.path.exists('/data/ntuples/las'):
#    processors.append( ReadLaser(processingDir='/data/ntuples/las',
#                                 diode_num=0,
#                                 verbose=False) )
#else:
#    processors.append( ReadLaser(diode_num=0, verbose=False ) )
#processors.append( CleanLaser() ) 

#processors.append( Print(region='TILECAL_LBA_m34_c39', verbose=True) )
schema='sqlite://;schema=tileSqlite.db;dbname=CONDBR2'
if not os.path.isfile("tileSqlite.db"): 
    if os.path.isfile(getResultDirectory()+"tileSqlite.db"): # Makes Sacha happy!
        schema='sqlite://;schema='+getResultDirectory()+'tileSqlite.db;dbname=CONDBR2'
    else:
        schema='COOLOFL_TILE/CONDBR2'

processors.append( ReadCalFromCool( schema=schema,
                                    folder='/TILE/OFL02/CALIB/CES',
                                    runType = 'Las_REF',
                                    tag = 'RUN2-HLT-UPD1-01',
                                    verbose=True) )

#processors.append( ReadCalibFromCool( runType = 'Las_REF',
#                                    schema = 'OFL',
#                                    folder = 'CALIB/CES',
#                                    tag = 'UPD1',
#                                    verbose = True) )




# processors.append( ReadCalibFromCool( runType = 'cesium',
#                                     schema = 'OFL',
#                                     #schema = 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2',
#                                     folder = 'CALIB/CES',
#                                     #folder = '/TILE/OFL02/CALIB/CES', #For use with SQL file
#                                     tag='UPD4',
#                                     verbose = False) )

processors.append( FillBetaHVNom() )

if doClermont:
    processors.append( getFiberShifts(n_iter=3, verbose=True) )
    processors.append( getPMTShiftsObsolete() )
# processors.append( do_fiber_plot(doEps = True) )
else:
    processors.append( getGlobalShiftsDirect(siglim=2.0,n_iter=3,verbose=False) )
    processors.append( getFiberShiftsDirect(siglim=2.0, n_iter=3,verbose=False) )
    processors.append( getPMTShiftsDirect() )
    # processors.append( do_global_plot(doEps = True) )
    # processors.append( do_fiber_plot(doEps = True) )

processors.append(do_average_plot(f=(lambda event: -10000. if (not event.data.has_key('deviation'))
                                     else event.data['deviation'] )))



doPMTPlots = False

if region == None:
    region=''

if doPMTPlots:

    if region == '':
        processors.append( do_pmts_plot_2gains(limit=1.))  # All modules
    else:
        if region.find('LBA')>-1:
            processors.append( do_pmts_plot_2gains(limit=1., part=LBA ))  # LBA modules
        if region.find('LBC')>-1:
            processors.append( do_pmts_plot_2gains(limit=1., part=LBC ))  # LBC modules
        if region.find('EBA')>-1:
            processors.append( do_pmts_plot_2gains(limit=1., part=EBA ))  # EBA modules
        if region.find('EBC')>-1:
            processors.append( do_pmts_plot_2gains(limit=1., part=EBC ))  # EBC modules



Go( processors )

