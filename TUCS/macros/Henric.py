#!/usr/bin/env python
# Atuh: Henric
# date: a Sunday morning in January 2012
#
# Even though its not FORTRAN, its good to be able to print....
#        1         2         3         4         5         6         7         8
#2345678901234567890123456789012345678901234567890123456789012345678901234567890

import os, sys
os.chdir(os.getenv('TUCS','.'))
exec(open('src/laser/laserGetOpt.py').read(), globals())
exec(open('src/load.py').read(), globals()) # don't remove this!

processors = []

processors.append( Use(runs, run2=enddate, filter=filt_pos, runType='Las',
                       region=region, TWOInput=twoinput) )

processors.append( ReadBchFromCool( schema='COOLOFL_TILE/CONDBR2',
                                    folder='/TILE/OFL02/STATUS/ADC',
                                    tag='UPD4',
                                    Fast=True,
                                    storeADCinfo=True) )
if os.path.exists('/data/ntuples/las'):
    processors.append( ReadLaser(processingDir='/data/ntuples/las',
                                 diode_num_lg=0, diode_num_hg=0,
                                 doPisa=usePisa,
                                 verbose=False) )
else:
    processors.append( ReadLaser(diode_num=0, verbose=False,
                                 doPisa=usePisa) )
processors.append( CleanLaser() )

#processors.append( Print(region='TILECAL_LBA_m34_c39', verbose=True) )

#processors.append( ReadCalFromCool( runType = 'Las',
#                                    schema = 'COOLOFL_TILE/CONDBR2',
##                                    schema = 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2',
#                                    folder = '/TILE/OFL02/CALIB/LAS/LIN',
#                                    tag = 'UPD4',
#                                    verbose = True) )


processors.append( Use(run=date, run2=enddate, runType='cesium', region=region,
                       cscomment='sol+tor', keepOnlyActive=True, TWOInput=twoinput,
                       allowC10Errors = True) )

processors.append( ReadCsFile(normalize=True, skipITC=True, verbose=False) )

#processors.append( Print(region='TILECAL_LBA_m34_c00', verbose=True) )

processors.append( ReadCalFromCool( runType='integrator',
                                    schema='COOLOFL_TILE/CONDBR2',
                                    #schema = 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2',
                                    folder='/TILE/OFL02/INTEGRATOR',
                                    tag = 'UPD4',
                                    verbose = False) )

processors.append( ReadCalFromCool( runType = 'cesium',
                                    schema = 'COOLOFL_TILE/CONDBR2',
                                    #schema = 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2',
                                    folder = '/TILE/OFL02/CALIB/CES',
                                    tag = 'UPD4',
                                    verbose = False) )


processors.append( FillBetaHVNom() )

doOficialRefs = False

if doOficialRefs:
    schema = 'COOLOFL_TILE/CONDBR2'
    tag = 'UPD4'
else:
    schema = 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2'
    tag = 'RUN2-HLT-UPD1-01'

processors.append( ReadCalFromCool( runType = 'Las_REF',
                                    schema = schema,
                                    folder = '/TILE/OFL02/CALIB/CES',
                                    tag = tag, verbose = True) )

doClermont = False
if doClermont:
    processors.append( getFiberShifts(n_iter=3, verbose=True) )
    processors.append( getPMTShiftsObsolete() )
else:
    processors.append( getGlobalShiftsDirect(siglim=2.0,n_iter=3,verbose=False) )
    processors.append( getFiberShiftsDirect(siglim=2.0, n_iter=3,verbose=False) )
    processors.append( getPMTShiftsDirect(usePisa=True) )

#    processors.append( do_global_plot(doEps = True) )
#    processors.append( do_fiber_plot_henric(doEps = True) )

processors.append( Vincent() )

doPMTPlots = False
if doPMTPlots:
    if region == None:
        processors.append( do_pmts_plot_LasCs(limit=1, ymin=-10., ymax=+5.))  # All modules
    else:
        if region.find('LBA')>-1:
            processors.append( do_pmts_plot_LasCs(limit=1., part=LBA, ymin=-10., ymax=+10. ))  # LBA modules
        if region.find('LBC')>-1:
            processors.append( do_pmts_plot_LasCs(limit=1., part=LBC, ymin=-10., ymax=+10. ))  # LBC modules
        if region.find('EBA')>-1:
            processors.append( do_pmts_plot_LasCs(limit=1., part=EBA, ymin=-10., ymax=+10. ))  # EBA modules
        if region.find('EBC')>-1:
            processors.append( do_pmts_plot_LasCs(limit=1., part=EBC, ymin=-10., ymax=+10. ))  # EBC modules

doChanPlot = False
if doChanPlot:
    if region==None or region.find('LBA')!=-1:

        processors.append( do_LasCs_plots(part=LBA, mod= 4, chan=44))
        processors.append( do_LasCs_plots(part=LBA, mod=16, chan=33))
        processors.append( do_LasCs_plots(part=LBA, mod=21, chan=19))
        processors.append( do_LasCs_plots(part=LBA, mod=34, chan= 2))
        processors.append( do_LasCs_plots(part=LBA, mod=37, chan=19))
        processors.append( do_LasCs_plots(part=LBA, mod=38, chan=15))
        processors.append( do_LasCs_plots(part=LBA, mod=53, chan=33))

        processors.append( do_chan_plot_henric(limit=1, part=LBA, mod= 4, chan=44, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=LBA, mod=16, chan=33, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=LBA, mod=21, chan=19, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=LBA, mod=34, chan= 2, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=LBA, mod=37, chan=19, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=LBA, mod=38, chan=15, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=LBA, mod=53, chan=33, doEps = True))

    if region==None or region.find('LBC')!=-1:

        processors.append( do_LasCs_plots(part=LBC, mod=14, chan= 1))
        processors.append( do_LasCs_plots(part=LBC, mod=24, chan= 3))
        processors.append( do_LasCs_plots(part=LBC, mod=24, chan= 4))
        processors.append( do_LasCs_plots(part=LBC, mod=24, chan= 5))
        processors.append( do_LasCs_plots(part=LBC, mod=26, chan=38))
        processors.append( do_LasCs_plots(part=LBC, mod=55, chan=27))
        processors.append( do_LasCs_plots(part=LBC, mod=57, chan= 6))
        processors.append( do_LasCs_plots(part=LBC, mod=57, chan= 7))
        processors.append( do_LasCs_plots(part=LBC, mod=57, chan= 8))
        processors.append( do_LasCs_plots(part=LBC, mod=59, chan=33))
        processors.append( do_chan_plot_henric(limit=1, part=LBC, mod=14, chan= 1, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=LBC, mod=24, chan= 3, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=LBC, mod=24, chan= 4, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=LBC, mod=24, chan= 5, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=LBC, mod=26, chan=38, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=LBC, mod=55, chan=27, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=LBC, mod=57, chan= 6, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=LBC, mod=57, chan= 7, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=LBC, mod=57, chan= 8, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=LBC, mod=59, chan=33, doEps = True))


    if region==None or region.find('EBA')!=-1:

        processors.append( do_LasCs_plots(part=EBA, mod=57, chan=22))
        processors.append( do_LasCs_plots(part=EBA, mod=63, chan=15))
        processors.append( do_chan_plot_henric(limit=1, part=EBA, mod=57, chan=22, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=EBA, mod=63, chan=15, doEps = True))


    if region==None or region.find('EBC')!=-1:
        processors.append( do_LasCs_plots(part=EBC, mod= 5, chan=20))
        processors.append( do_LasCs_plots(part=EBC, mod= 9, chan=40))
        processors.append( do_LasCs_plots(part=EBC, mod=13, chan=37))
        processors.append( do_LasCs_plots(part=EBC, mod=18, chan= 4))
        processors.append( do_LasCs_plots(part=EBC, mod=20, chan=10))
        processors.append( do_LasCs_plots(part=EBC, mod=29, chan=15))
        processors.append( do_LasCs_plots(part=EBC, mod=30, chan=22))
        processors.append( do_LasCs_plots(part=EBC, mod=38, chan= 1))
        processors.append( do_LasCs_plots(part=EBC, mod=40, chan= 0))
        processors.append( do_LasCs_plots(part=EBC, mod=43, chan= 4))
        processors.append( do_LasCs_plots(part=EBC, mod=58, chan=21))
        processors.append( do_LasCs_plots(part=EBC, mod=58, chan=22))
        processors.append( do_LasCs_plots(part=EBC, mod=58, chan=23))
        processors.append( do_LasCs_plots(part=EBC, mod=63, chan=15))
        processors.append( do_chan_plot_henric(limit=1, part=EBC, mod= 5, chan=20, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=EBC, mod= 9, chan=40, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=EBC, mod=13, chan=37, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=EBC, mod=18, chan= 4, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=EBC, mod=20, chan=10, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=EBC, mod=29, chan=15, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=EBC, mod=30, chan=22, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=EBC, mod=38, chan= 1, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=EBC, mod=40, chan= 0, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=EBC, mod=43, chan= 4, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=EBC, mod=58, chan=21, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=EBC, mod=58, chan=22, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=EBC, mod=58, chan=23, doEps = True))
        processors.append( do_chan_plot_henric(limit=1, part=EBC, mod=63, chan=15, doEps = True))


#for part in [LBA, LBC]:
#    for module in range(1,65):
#        processors.append(  do_LasCs_plots(part=part, mod=module, chan= 6) ) # A BC-cell


#processors.append(  do_LasCs_plots(part=LBA, mod= 3, chan= 7) )
#processors.append(  do_LasCs_plots(part=LBA, mod=21, chan=19) )
#processors.append(  do_LasCs_plots(part=LBA, mod=37, chan= 1) )
#processors.append(  do_LasCs_plots(part=LBA, mod=48, chan=45) )
#processors.append(  do_LasCs_plots(part=EBA, mod=50, chan=22) )
#processors.append(  do_LasCs_plots(part=EBC, mod= 8, chan=35) )

#for module in range(64):
#    for chan in [6,7,8,9,10,11]:
#        processors.append(  do_LasCs_plots(part=EBA, mod=module+1, chan=chan) )


# # processors.append(  do_LasCs_plots(part=EBC, mod= 4, chan= 1) )
# processors.append(  do_LasCs_plots(part=EBC, mod= 5, chan= 4) )
# processors.append(  do_LasCs_plots(part=EBC, mod=13, chan=37) )
# # processors.append(  do_LasCs_plots(part=EBC, mod=20, chan= 0) )
# # processors.append(  do_LasCs_plots(part=EBC, mod=24, chan= 1) )
# # processors.append(  do_LasCs_plots(part=EBC, mod=30, chan=13) )
# processors.append(  do_LasCs_plots(part=EBC, mod=31, chan=36) )
# # processors.append(  do_LasCs_plots(part=EBC, mod=35, chan= 0) )
# # processors.append(  do_LasCs_plots(part=EBC, mod=36, chan= 5) )
# # processors.append(  do_LasCs_plots(part=EBC, mod=36, chan= 6) )
# # processors.append(  do_LasCs_plots(part=EBC, mod=40, chan=13) )
# # processors.append(  do_LasCs_plots(part=EBC, mod=43, chan= 4) )
# processors.append(  do_LasCs_plots(part=EBC, mod=46, chan=23) )
# # processors.append(  do_LasCs_plots(part=EBC, mod=51, chan=13) )
# processors.append(  do_LasCs_plots(part=EBC, mod=51, chan=14) )
# processors.append(  do_LasCs_plots(part=EBC, mod=53, chan=21) )
# processors.append(  do_LasCs_plots(part=EBC, mod=53, chan=39) )
# # processors.append(  do_LasCs_plots(part=EBC, mod=54, chan= 1) )
# processors.append(  do_LasCs_plots(part=EBC, mod=56, chan=36) )
# # processors.append(  do_LasCs_plots(part=EBC, mod=58, chan= 3) )
# # processors.append(  do_LasCs_plots(part=EBC, mod=60, chan= 6) )
# processors.append(  do_LasCs_plots(part=EBC, mod=60, chan=10) )
# # processors.append(  do_LasCs_plots(part=EBC, mod=61, chan= 1) )
# processors.append(  do_LasCs_plots(part=EBC, mod=61, chan=17) )
# processors.append(  do_LasCs_plots(part=EBC, mod=61, chan=22) )
# # processors.append(  do_LasCs_plots(part=EBC, mod=63, chan= 1) )
# processors.append(  do_LasCs_plots(part=EBC, mod=63, chan= 7) )
# processors.append(  do_LasCs_plots(part=EBC, mod=63, chan= 9) )
# processors.append(  do_LasCs_plots(part=EBC, mod=63, chan=11) )
# # processors.append(  do_LasCs_plots(part=EBC, mod=63, chan=13) )
# # processors.append(  do_LasCs_plots(part=EBC, mod=63, chan=13) )
# processors.append(  do_LasCs_plots(part=EBC, mod=63, chan=15) )
# processors.append(  do_LasCs_plots(part=EBC, mod=64, chan=31) )
# processors.append(  do_LasCs_plots(part=EBC, mod=64, chan=32) )

# processors.append(  do_LasCs_plots(part=LBA, mod= 1, chan=25) )
# processors.append(  do_LasCs_plots(part=LBA, mod= 2, chan=33) )
# processors.append(  do_LasCs_plots(part=LBA, mod= 2, chan=35) )
# processors.append(  do_LasCs_plots(part=LBA, mod= 4, chan=44) )
# processors.append(  do_LasCs_plots(part=LBA, mod= 6, chan=26) )
# processors.append(  do_LasCs_plots(part=LBA, mod= 9, chan= 9) ) # Scaha Cs concern 03/12
# processors.append(  do_LasCs_plots(part=LBA, mod=13, chan=35) )
# processors.append(  do_LasCs_plots(part=LBA, mod=14, chan=36) )
# processors.append(  do_LasCs_plots(part=LBA, mod=14, chan=46) )
# processors.append(  do_LasCs_plots(part=LBA, mod=15, chan=16) )
# processors.append(  do_LasCs_plots(part=LBA, mod=17, chan= 6) )
# processors.append(  do_LasCs_plots(part=LBA, mod=17, chan=14) )
# processors.append(  do_LasCs_plots(part=LBA, mod=17, chan=16) )
# processors.append(  do_LasCs_plots(part=LBA, mod=17, chan=26) )
# processors.append(  do_LasCs_plots(part=LBA, mod=18, chan=13) )
# processors.append(  do_LasCs_plots(part=LBA, mod=19, chan= 2) )
# processors.append(  do_LasCs_plots(part=LBA, mod=19, chan=13) ) # Sacha
# processors.append(  do_LasCs_plots(part=LBA, mod=19, chan=23) )
# processors.append(  do_LasCs_plots(part=LBA, mod=21, chan=19) )
# processors.append(  do_LasCs_plots(part=LBA, mod=21, chan=34) )
# processors.append(  do_LasCs_plots(part=LBA, mod=23, chan= 3) )
# processors.append(  do_LasCs_plots(part=LBA, mod=23, chan=42) )
# processors.append(  do_LasCs_plots(part=LBA, mod=23, chan=45) )
# processors.append(  do_LasCs_plots(part=LBA, mod=29, chan= 1) )
# processors.append(  do_LasCs_plots(part=LBA, mod=29, chan= 2) )
# processors.append(  do_LasCs_plots(part=LBA, mod=33, chan=16) )
# processors.append(  do_LasCs_plots(part=LBA, mod=37, chan= 1) )
# processors.append(  do_LasCs_plots(part=LBA, mod=37, chan= 6) ) # Loic's channel
# processors.append(  do_LasCs_plots(part=LBA, mod=37, chan=19) )
# processors.append(  do_LasCs_plots(part=LBA, mod=43, chan= 1) )
# processors.append(  do_LasCs_plots(part=LBA, mod=43, chan=24) )
# processors.append(  do_LasCs_plots(part=LBA, mod=44, chan=23) )
# processors.append(  do_LasCs_plots(part=LBA, mod=47, chan= 2) )
# processors.append(  do_LasCs_plots(part=LBA, mod=48, chan=45) )
# processors.append(  do_LasCs_plots(part=LBA, mod=49, chan= 4) )# Sacha
# processors.append(  do_LasCs_plots(part=LBA, mod=50, chan=18) )
# processors.append(  do_LasCs_plots(part=LBA, mod=50, chan=23) )
# processors.append(  do_LasCs_plots(part=LBA, mod=50, chan=26) )
# processors.append(  do_LasCs_plots(part=LBA, mod=51, chan= 9) )
# processors.append(  do_LasCs_plots(part=LBA, mod=51, chan=12) )
# processors.append(  do_LasCs_plots(part=LBA, mod=53, chan=16) )
# processors.append(  do_LasCs_plots(part=LBA, mod=59, chan=12) )
# processors.append(  do_LasCs_plots(part=LBA, mod=59, chan=38) )
# processors.append(  do_LasCs_plots(part=LBA, mod=61, chan=13) )
# processors.append(  do_LasCs_plots(part=LBA, mod=61, chan=13) )
# processors.append(  do_LasCs_plots(part=LBA, mod=62, chan=18) )

# processors.append(  do_LasCs_plots(part=LBC, mod= 2, chan=38) )
# processors.append(  do_LasCs_plots(part=LBC, mod= 2, chan=40) )
# processors.append(  do_LasCs_plots(part=LBC, mod= 3, chan=41) )
# processors.append(  do_LasCs_plots(part=LBC, mod= 3, chan=44) )
# processors.append(  do_LasCs_plots(part=LBC, mod= 4, chan=20) )
# processors.append(  do_LasCs_plots(part=LBC, mod= 9, chan=40) )
# processors.append(  do_LasCs_plots(part=LBC, mod=11, chan= 7) )# Sacha
# processors.append(  do_LasCs_plots(part=LBC, mod=11, chan=28) )
# processors.append(  do_LasCs_plots(part=LBC, mod=14, chan= 1) )
# processors.append(  do_LasCs_plots(part=LBC, mod=16, chan=26) )
# processors.append(  do_LasCs_plots(part=LBC, mod=18, chan=13) )
# processors.append(  do_LasCs_plots(part=LBC, mod=21, chan=47) )
# processors.append(  do_LasCs_plots(part=LBC, mod=23, chan=13) )
# processors.append(  do_LasCs_plots(part=LBC, mod=26, chan=34) )
# processors.append(  do_LasCs_plots(part=LBC, mod=27, chan=17) )
# processors.append(  do_LasCs_plots(part=LBC, mod=28, chan= 7) )
# processors.append(  do_LasCs_plots(part=LBC, mod=28, chan=35) )
# processors.append(  do_LasCs_plots(part=LBC, mod=29, chan=26) )
# processors.append(  do_LasCs_plots(part=LBC, mod=36, chan=24) )
# processors.append(  do_LasCs_plots(part=LBC, mod=37, chan=32) )
# processors.append(  do_LasCs_plots(part=LBC, mod=38, chan=21) )
# processors.append(  do_LasCs_plots(part=LBC, mod=38, chan=25) )
# processors.append(  do_LasCs_plots(part=LBC, mod=42, chan=40) )
# processors.append(  do_LasCs_plots(part=LBC, mod=43, chan=36) )
# processors.append(  do_LasCs_plots(part=LBC, mod=44, chan=18) )
# processors.append(  do_LasCs_plots(part=LBC, mod=44, chan=23) )
# processors.append(  do_LasCs_plots(part=LBC, mod=44, chan=36) )
# processors.append(  do_LasCs_plots(part=LBC, mod=44, chan=38) )
# processors.append(  do_LasCs_plots(part=LBC, mod=45, chan=29) )
# processors.append(  do_LasCs_plots(part=LBC, mod=45, chan=47) )
# processors.append(  do_LasCs_plots(part=LBC, mod=46, chan=37) )
# processors.append(  do_LasCs_plots(part=LBC, mod=46, chan=41) )
# processors.append(  do_LasCs_plots(part=LBC, mod=49, chan=27) )
# processors.append(  do_LasCs_plots(part=LBC, mod=52, chan= 8) )# Sacha
# processors.append(  do_LasCs_plots(part=LBC, mod=55, chan= 2) )
# processors.append(  do_LasCs_plots(part=LBC, mod=55, chan= 3) )
# processors.append(  do_LasCs_plots(part=LBC, mod=57, chan=13) )
# processors.append(  do_LasCs_plots(part=LBC, mod=58, chan=21) )
# processors.append(  do_LasCs_plots(part=LBC, mod=59, chan= 4) )
#
# processors.append(  do_LasCs_plots(part=LBC, mod=60, chan=16) )
# processors.append(  do_LasCs_plots(part=LBC, mod=60, chan=34) )
# processors.append(  do_LasCs_plots(part=LBC, mod=61, chan=13) )
# processors.append(  do_LasCs_plots(part=LBC, mod=62, chan=23) )
# processors.append(  do_LasCs_plots(part=LBC, mod=62, chan=32) )
# processors.append(  do_LasCs_plots(part=LBC, mod=62, chan=39) )
# processors.append(  do_LasCs_plots(part=LBC, mod=63, chan=41) )

# # All ITC:
#for part in [EBA, EBC]:
#    for module in range(1,65):
#        processors.append(  do_LasCs_plots(part=part, mod=module, chan= 0) ) # E3 or MBTS
#        processors.append(  do_LasCs_plots(part=part, mod=module, chan= 1) ) # E4

#         processors.append(  do_LasCs_plots(part=part, mod=module, chan= 2) ) # D4
#         processors.append(  do_LasCs_plots(part=part, mod=module, chan= 3) ) # D4

#         processors.append(  do_LasCs_plots(part=part, mod=module, chan= 5) ) # C10
#         processors.append(  do_LasCs_plots(part=part, mod=module, chan= 6) ) # C10

#         processors.append(  do_LasCs_plots(part=part, mod=module, chan=12) ) # E1
#         processors.append(  do_LasCs_plots(part=part, mod=module, chan=13) ) # E2

Go( processors )
# The End

