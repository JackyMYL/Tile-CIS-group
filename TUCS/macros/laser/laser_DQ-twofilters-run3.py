#!/usr/bin/env python
# @author:  Henric
# @date:    somewhere in 2011
# @purpose: makes nice laser trend plots
#
# Even though its not FORTRAN, its good to be able to print....
#        1         2         3         4         5         6         7         8
#2345678901234567890123456789012345678901234567890123456789012345678901234567890

[LBA, LBC, EBA, EBC] = [1, 2, 3, 4]

import os, sys

os.chdir(os.getenv('TUCS','.'))

exec(open('src/load.py').read(), globals()) # don't remove this!
exec(open('src/laser/laserGetOpt.py').read(), globals())

# Laser Argument class
localArgParser=laserArgs(verbose=True)
# Add local arguments that are specific to this macro
#localArgParser.add_local_arg('--newArg', action='store_true',  default=False, arghelp='New argument \n')
# Get arguments from parser
localArgs=localArgParser.args_from_parser()
#newArg=localArgs.newArg

if date != '':
    runs = str(date)
print(runs)

processors = [ Use(runs, run2=enddate, filter=filt_pos, runType='Las', region=region, TWOInput=twoinput, amp='15000') ]

if not doDirect:
    usePisa = True

if os.path.exists('/data/ntuples/las'):
    b = ReadLaser(processingDir='/data/ntuples/las',
                  diode_num_lg=12,
                  diode_num_hg=13,
                  doPisa=usePisa) #, verbose=True
else:
    b = ReadLaser(diode_num_lg=12, diode_num_hg=13, doPisa=usePisa)

#b = ReadLaser(diode_num=0, doPisa=usePisa)

processors.append( b )

processors.append( do_diode_plot(doEps=plotEps) )

processors.append( CleanLaser() )

processors.append( ReadBchFromCool( schema='COOLOFL_TILE/CONDBR2',
                                    folder='/TILE/OFL02/STATUS/ADC',
                                    tag='UPD4',
                                    Fast=True,
                                    storeADCinfo=True ) )

schema='sqlite://;schema=tileSqlite.db;dbname=CONDBR2'
if not os.path.isfile("tileSqlite.db"):
    if os.path.isfile(getResultDirectory()+"tileSqlite.db"): # Makes Sacha happy!
        schema='sqlite://;schema='+getResultDirectory()+'tileSqlite.db;dbname=CONDBR2'
    else:
        schema='COOLOFL_TILE/CONDBR2'

schema='sqlite://;schema=tileSqlite.db;dbname=CONDBR2'
tag='RUN2-HLT-UPD1-01'
#schema='sqlite://;schema=/afs/cern.ch/user/k/klimek/public/Laser/Reference/Reference_2018/Reprocessing_2018/tileSqlite_Reprocessing_Full2018_v2.db;dbname=CONDBR2' ##latest version 2018 for combined method
#tag='TileOfl02CalibCes-RUN2-UPD4-20'

processors.append( ReadCalFromCool( schema=schema,
                                    folder='/TILE/OFL02/CALIB/CES',
                                    runType = 'Las_REF',
                                    tag = tag,
                                    verbose=True) )

processors.append( FillBetaHVNom() )

if doDirect:
    processors.append( getGlobalShiftsDirect(siglim=2.0, n_iter=3, verbose=True) )
    processors.append( getFiberShiftsDirect(siglim=1.5, n_iter=2, verbose=True) )
    processors.append( getPMTShiftsDirect(usePisa=False) )
else:
    processors.append( getGlobalShiftsCombined(siglim=2.0, n_iter=3, verbose=True) )
    processors.append( getFiberShiftsCombined(siglim=2.0, n_iter=3, verbose=True) )
    processors.append( getPMTShiftsDirect(usePisa=False) )

processors.append( do_global_plot(doEps = plotEps) )
processors.append( getFiberTotals() )
processors.append( do_fiber_plot(doEps = plotEps) )




processors.append(do_diode_plot())

#processors.append(do_average_plot(f=(lambda event: -10000. if (not 'deviation' in event.data)
#                                     else event.data['deviation'] ), cells=['E1', 'E2', 'E3', 'E4']))

processors.append( getBadChannels() )


doPMTPlots   = True
doHVPlot     = False
doChanPlot   = False
doITC        = False
doProblems   = True

if region == None:
    region=''


if doPMTPlots:
    if region == '':
        processors.append( do_pmts_plot_2gains(limit=1., doEps=plotEps ))  # All modules
    else:
        if region.find('LBA')>-1:
            processors.append( do_pmts_plot_2gains(limit=1., part=LBA, doEps=plotEps ))  # LBA modules
        if region.find('LBC')>-1:
            processors.append( do_pmts_plot_2gains(limit=1., part=LBC, doEps=plotEps ))  # LBC modules
        if region.find('EBA')>-1:
            processors.append( do_pmts_plot_2gains(limit=1., part=EBA, doEps=plotEps ))  # EBA modules
        if region.find('EBC')>-1:
            processors.append( do_pmts_plot_2gains(limit=1., part=EBC, doEps=plotEps ))  # EBC modules


if doITC:
#    processors.append( set_chan_plot_itc(limit=1, doEps = plotEps) )
    processors.append( set_chan_plot_itc() )

if doProblems:
    badProblems = ['ADC masked (unspecified)', 'ADC dead', "No data", "Very large HF noise", "Stuck bit", "Severe stuck bit",
                   'Severe data corruption',
                   'Channel masked (unspecified)','No PMT connected', 'Wrong HV']

#    badProblems = ['Bad laser calibration','No laser calibration']
#    processors.append( set_chan_plot_problems(limit=1, problems=badProblems, doEps = plotEps))
    processors.append( set_chan_plot_problems(problems=badProblems))


if doChanPlot:
    if region=='' or region.find('LBA')!=-1:
        
        for chan in range(47):
            processors.append( set_chan_plot(limit=1, part=LBA, mod=14, chan=chan, doEps = plotEps))
        
        processors.append( set_chan_plot(limit=1, part=LBA, mod=2,  chan=6,  doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBA, mod=12, chan=4, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBA, mod=21, chan=45, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBA, mod=23, chan=11, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBA, mod=45, chan=6,  doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBA, mod=49, chan=4,  doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBA, mod=52, chan=1,  doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBA, mod=64, chan=29, doEps = plotEps))
        # processors.append( set_chan_plot(limit=1, part=LBA, mod=37, chan=19, doEps = plotEps))
        # processors.append( set_chan_plot(limit=1, part=LBA, mod=41, chan=32, doEps = plotEps))
        # processors.append( set_chan_plot(limit=1, part=LBA, mod=42, chan=12, doEps = plotEps))

        # processors.append( set_chan_plot(limit=1, part=LBA, mod=35, chan=3, doEps = plotEps)) # R11187 pmt
        # processors.append( set_chan_plot(limit=1, part=LBA, mod=37, chan=1, doEps = plotEps)) # R11187 pmt

    if region=='' or region.find('LBC')!=-1:
        processors.append( set_chan_plot(limit=1, part=LBC, mod=1,  chan=25, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=2,  chan=38, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=8,  chan=3,  doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=10, chan=9,  doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=10, chan=23, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=10, chan=35, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=10, chan=37, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=13, chan=15, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=13, chan=26, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=18, chan=13, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=19, chan=22, doEps = plotEps))
        # processors.append( set_chan_plot(limit=1, part=LBC, mod=20, chan=28, doEps = plotEps))
        # processors.append( set_chan_plot(limit=1, part=LBC, mod=20, chan=39, doEps = plotEps))
        # processors.append( set_chan_plot(limit=1, part=LBC, mod=20, chan=44, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=23, chan=20, doEps = plotEps))
        # processors.append( set_chan_plot(limit=1, part=LBC, mod=27, chan=45, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=28, chan=4,  doEps = plotEps))
        # processors.append( set_chan_plot(limit=1, part=LBC, mod=28, chan=35,  doEps = plotEps))
        # processors.append( set_chan_plot(limit=1, part=LBC, mod=29, chan=26, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=43, chan=24, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=44, chan=12, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=46, chan=4,  doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=47, chan=35, doEps = plotEps))
        # processors.append( set_chan_plot(limit=1, part=LBC, mod=56, chan=10, doEps = plotEps))
        # processors.append( set_chan_plot(limit=1, part=LBC, mod=59, chan=33, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=59, chan=26, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=62, chan=8,  doEps = plotEps))

#        for chan in range(48):
#            processors.append( set_chan_plot(limit=1, part=LBC, mod= 6, chan=chan, doEps = plotEps))
#            processors.append( set_chan_plot(limit=1, part=LBC, mod=17, chan=chan, doEps = plotEps))
#        for chan in [1, 3, 5, 7, 9,11,13,15,17,19,21,23,25,27,29,33,35,37,39,41,45,47]:
#            processors.append( set_chan_plot(limit=1, part=LBC, mod=17, chan=chan, doEps = plotEps))
        pass

    if region=='' or region.find('EBA')!=-1:

        # processors.append( set_chan_plot(limit=1, part=EBA, mod= 3, chan=7, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBA, mod=7,  chan=28, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBA, mod=16, chan=17, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBA, mod=19, chan=41, doEps = plotEps))

        # processors.append( set_chan_plot(limit=1, part=EBA, mod=34, chan=8,  doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBA, mod=39, chan=31, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBA, mod=42, chan=30, doEps = plotEps))
        # processors.append( set_chan_plot(limit=1, part=EBA, mod=49, chan=00, doEps = plotEps))
        # processors.append( set_chan_plot(limit=1, part=EBA, mod=49, chan=31, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBA, mod=50, chan=20, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBA, mod=50, chan=31, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBA, mod=55, chan=22, doEps = plotEps))
        # processors.append( set_chan_plot(limit=1, part=EBA, mod=61, chan=10, doEps = plotEps))
        # processors.append( set_chan_plot(limit=1, part=EBA, mod=61, chan=16, doEps = plotEps))
        # processors.append( set_chan_plot(limit=1, part=EBA, mod=63, chan=15, doEps = plotEps))
        # processors.append( set_chan_plot(limit=1, part=EBA, mod=53, chan=1, doEps = plotEps)) # R11187 pmt
        processors.append( set_chan_plot(limit=1, part=EBA, mod=64, chan=3,  doEps = plotEps))

    if region=='' or region.find('EBC')!=-1:
        processors.append( set_chan_plot(limit=1, part=EBC, mod=1,  chan=21, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=5,  chan=4, doEps = plotEps))
        # processors.append( set_chan_plot(limit=1, part=EBC, mod=12, chan=36, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=13, chan=3,  doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=15, chan=16, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=18, chan=4,  doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=19, chan=12, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=22, chan=16, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=23, chan=3,  doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=23, chan=31, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=23, chan=36, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=24, chan=12, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=26, chan=1,  doEps = plotEps))
        # processors.append( set_chan_plot(limit=1, part=EBC, mod=31, chan=41, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=34, chan=12, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=36, chan=0,  doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=36, chan=10, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=37, chan=7,  doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=37, chan=11, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=37, chan=12, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=39, chan=4,  doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=39, chan=31, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=40, chan=4, doEps = plotEps))
        # processors.append( set_chan_plot(limit=1, part=EBC, mod=40, chan=3, doEps = plotEps))
        # processors.append( set_chan_plot(limit=1, part=EBC, mod=40, chan=15, doEps = plotEps))
        # processors.append( set_chan_plot(limit=1, part=EBC, mod=40, chan=16, doEps = plotEps))
        # processors.append( set_chan_plot(limit=1, part=EBC, mod=46, chan=7, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=53, chan=13, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=53, chan=16, doEps = plotEps))
        # processors.append( set_chan_plot(limit=1, part=EBC, mod=55, chan=6, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=56, chan=41, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=61, chan=6,  doEps = plotEps))
        # processors.append( set_chan_plot(limit=1, part=EBC, mod=64, chan=31, doEps = plotEps))
        # 
        #              processors.append( set_chan_plot(limit=1, part=EBC, mod=57, chan=37, doEps = plotEps))
        #        for chan in [1,3,5,7,9,11,13,15,17,21,23,32,35,36,37,40]:
        #        for chan in [0,2,4,6,8,10,12,14,16,20,22,30,31,38,39,41]:
        #            processors.append( set_chan_plot(limit=1, part=EBC, mod=23, chan=chan, doEps = plotEps))
        #            processors.append( set_chan_plot(limit=1, part=EBC, mod=24, chan=chan, doEps = plotEps))

        pass

processors.append( do_chan_plot_new(limit=1., doEps = plotEps))
#processors.append( Print(region='LBA_m14_c21',verbose=True) )
#processors.append( Print(region='LBA_m14_c30',verbose=True) )
#processors.append( Print(region='LBA_m14_c33',verbose=True) )

Go(processors,withMBTS=False)


