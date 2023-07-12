#!/usr/bin/env python 
# @author:  Henric
# @date:    somewhere in 2011
# @purpose: makes nice laser trend plots
#
# Even though its not FORTRAN, its good to be able to print....
#        1         2         3         4         5         6         7         8
#2345678901234567890123456789012345678901234567890123456789012345678901234567890

import os, sys
os.chdir(os.getenv('TUCS','.'))
exec(open('src/laser/laserGetOpt.py').read(), globals())
exec(open('src/load.py').read(), globals()) # don't remove this!

# Laser Argument class
localArgParser=laserArgs(verbose=True)
# Add local arguments that are specific to this macro
localArgParser.add_local_arg('--newArg', action='store_true',  default=False, arghelp='New argument \n')
# Get arguments from parser 
localArgs=localArgParser.args_from_parser()
newArg=localArgs.newArg

produce_wiki = False
runs = date
processors = [ Use(runs, run2=enddate, filter=filt_pos, runType='Las',
                   region=region, TWOInput=twoinput, amp='12000') ]

if os.path.exists('/data/ntuples/las'):
    b = ReadLaser(processingDir='/data/ntuples/las',
                  diode_num_lg=12, 
                  diode_num_hg=13, 
                  doPisa=usePisa) #, verbose=True
else:
    b = ReadLaser(diode_num_lg=12, diode_num_hg=13, doPisa=usePisa)

#b = ReadLaser(diode_num=0, doPisa=usePisa)

processors.append( b )

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

processors.append( ReadCalFromCool( schema=schema,
                                    folder='/TILE/OFL02/CALIB/CES',
                                    runType = 'Las_REF',
                                    tag = 'RUN2-HLT-UPD1-01',
                                    verbose=True) )

#processors.append( Print(region='LBC_m13',verbose=True) )
#processors.append( Print(region='LBA_m13',verbose=True) )


if not doCombined:
    processors.append( getGlobalShiftsDirect(siglim=2.0, n_iter=3, verbose=True) )
    processors.append( do_global_plot(doEps = True) )
    #
    processors.append( getFiberShiftsDirect(siglim=2.0, n_iter=3, verbose=True) )
    processors.append( do_fiber_plot(doEps = True) )
    # And finally the globally corrected PMT shifts, (stored in event.data['deviation'])
    processors.append( getPMTShiftsDirect(usePisa=True) )
else:
    processors.append( getGlobalShiftsCombined(siglim=2.0, n_iter=3, verbose=True) )   
    processors.append( do_global_plot(doEps = plotEps) )
    processors.append( getFiberShiftsCombined(siglim=2.0, n_iter=3, verbose=True) )
    processors.append( do_fiber_plot(doEps = plotEps) )   
    processors.append( getPMTShiftsDirect(usePisa=False) )

processors.append(do_diode_plot())

processors.append(do_average_plot(f=(lambda event: -10000. if (not event.data.has_key('deviation'))
                                     else event.data['deviation'] )))


processors.append( getBadChannels() )
processors.append( FillBetaHVNom() )

# The last steps are describing the plot production (default plots are .png)
#
# At each level, you could produce plots for few parts
# or for all the TileCal
#
# Below are some examples (uncomment what you want to try)

# processors.append( Print(region='LBA_m17_c26') )

doPMTPlots   = False
doHVPlot     = False
doChanPlot   = False
doITC        = False
doProblems   = False

if region == None:
    region=''

if doPMTPlots:
    if region == '':
        processors.append( do_pmts_plot_2gains(limit=1., ymin=-20., ymax=+15.))  # All modules
    else:
        if region.find('LBA')>-1:
            processors.append( do_pmts_plot_2gains(limit=1., part=LBA ))  # LBA modules
        if region.find('LBC')>-1:
            processors.append( do_pmts_plot_2gains(limit=1., part=LBC ))  # LBC modules
        if region.find('EBA')>-1:
            processors.append( do_pmts_plot_2gains(limit=1., part=EBA ))  # EBA modules
        if region.find('EBC')>-1:
            processors.append( do_pmts_plot_2gains(limit=1., part=EBC ))  # EBC modules

if doITC:
    processors.append( set_chan_plot_itc(limit=1, doEps = True) )

if doProblems:
    badProblems = ['ADC masked (unspecified)', 'ADC dead', "No data", "Very large HF noise", "Severe stuck bit",
                   'Severe data corruption',
                   'Channel masked (unspecified)','No PMT connected', 'Wrong HV']
    processors.append( set_chan_plot_problems(limit=1, problems=badProblems, doEps = True))



     

if doChanPlot:
    if region=='' or region.find('LBA')!=-1:
        processors.append( set_chan_plot(limit=1, part=LBA, mod=24, chan=17, doEps = True))
        processors.append( set_chan_plot(limit=1, part=LBA, mod=48, chan=45, doEps = True))
#        processors.append( set_chan_plot(limit=1, part=LBA, mod=17, chan=38, doEps = True))
#        processors.append( set_chan_plot(limit=1, part=LBA, mod=21, chan=32, doEps = True))

#        for chan in range(48):
#            processors.append( set_chan_plot(limit=1, part=LBA, mod= 6, chan=chan, doEps = True))
#            processors.append( set_chan_plot(limit=1, part=LBA, mod=17, chan=chan, doEps = True))
        for chan in [0, 2, 4, 6, 8,10,12,14,16,18,20,22,24,26,28,32,34,36,38,40,42,44,46]:
            processors.append( set_chan_plot(limit=1, part=LBA, mod=17, chan=chan, doEps = True))


    if region=='' or region.find('LBC')!=-1:
        processors.append( set_chan_plot(limit=1, part=LBC, mod=55, chan= 2, doEps = True))
#        processors.append( set_chan_plot(limit=1, part=LBC, mod=21, chan=36, doEps = True))
        
#        for chan in range(48):
#            processors.append( set_chan_plot(limit=1, part=LBC, mod= 6, chan=chan, doEps = True))
#            processors.append( set_chan_plot(limit=1, part=LBC, mod=17, chan=chan, doEps = True))
        for chan in [1, 3, 5, 7, 9,11,13,15,17,19,21,23,25,27,29,33,35,37,39,41,45,47]:
            processors.append( set_chan_plot(limit=1, part=LBC, mod=17, chan=chan, doEps = True))


    if region=='' or region.find('EBA')!=-1:
        processors.append( set_chan_plot(limit=1, part=EBA, mod= 4, chan=16, doEps = True))
        processors.append( set_chan_plot(limit=1, part=EBA, mod= 9, chan=16, doEps = True))
        processors.append( set_chan_plot(limit=1, part=EBA, mod=43, chan= 5, doEps = True))
#        processors.append( set_chan_plot(limit=1, part=EBA, mod=29, chan=07, doEps = True))


    if region=='' or region.find('EBC')!=-1:
        processors.append( set_chan_plot(limit=1, part=EBA, mod=53, chan=39, doEps = True))

#        processors.append( set_chan_plot(limit=1, part=EBC, mod=57, chan=37, doEps = True))
#        for chan in [1,3,5,7,9,11,13,15,17,21,23,32,35,36,37,40]:
        for chan in [0,2,4,6,8,10,12,14,16,20,22,30,31,38,39,41]:
            processors.append( set_chan_plot(limit=1, part=EBC, mod=23, chan=chan, doEps = True))
            processors.append( set_chan_plot(limit=1, part=EBC, mod=24, chan=chan, doEps = True))
            

        pass

#processors.append( set_chan_plot(limit=1, part=EBA, mod= 6, chan= 4, doEps = True))
Go(processors,withMBTS=False)
