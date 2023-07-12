#!/usr/bin/env python
# @author:  Henric
# @date:    somewhere in 2018
# @purpose: makes nice laser trend plots
#
# Even though its not FORTRAN, its good to be able to print....
#        1         2         3         4         5         6         7         8
#2345678901234567890123456789012345678901234567890123456789012345678901234567890

import os, sys

exec(open('src/load.py').read(), globals()) # don't remove this!
os.chdir(os.getenv('TUCS','.'))
exec(open('src/laser/laserGetOpt.py').read(), globals()) 
if not os.path.exists('results/output/'):
    os.makedirs('results/output/') 

[LBA, LBC, EBA, EBC] = [1, 2, 3, 4]

# Laser Argument class
localArgParser=laserArgs(verbose=True)
# Add local arguments that are specific to this macro
localArgParser.add_local_arg('--ReadlocalTilesqlite', action='store_true',  default=False,  arghelp='Read the reference value from a local tileSqlite \n')
# Get arguments from parser 
localArgs=localArgParser.args_from_parser()
ReadlocalTilesqlite=localArgs.ReadlocalTilesqlite

print("Arguments runs {} --date {} --enddate {} --outputTag {} --ReadlocalTilesqlite".format(runs,date,enddate,outputTag,ReadlocalTilesqlite))

if not doDirect:
    usePisa=True
    filt_pos='8'

# Definition of all the runs that need to be used for the study
if date != '':
    processors = [ Use(str(date), run2=enddate, filter=filt_pos, runType='Las', region=region, TWOInput=twoinput, amp='15000') ]
elif isinstance(runs, list):
    print("isinstance (runs,list) {} and we have a problem because we don't have a run list".format(isinstance(runs,list)))
    processors = [ Use(runs,  runType='Las', region=region, TWOInput=twoinput) ]
else:
    print("You should define a run list to run over or a time interval")
    exit()


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
processors.append( do_diode_plot(doEps=plotEps) )

# Read bad channels from COOL database
processors.append( ReadBchFromCool( schema='COOLOFL_TILE/CONDBR2',
                                    folder='/TILE/OFL02/STATUS/ADC',
                                    tag='UPD4',
                                    Fast=True,
                                    storeADCinfo=True ) )


if ReadlocalTilesqlite:
    schema='sqlite://;schema=data/laser/tileSqlite_files/tileSqlite_LasRef_2018_singleIOV.db;dbname=CONDBR2'
    tag='TileOfl02CalibCes-RUN2-UPD4-20'
else: 
    schema='COOLOFL_TILE/CONDBR2' # Read the reference values from the Conditions DB
    tag='TileOfl02CalibCes-RUN2-UPD4-24'


processors.append( ReadCalFromCool( schema=schema,
                                    folder='/TILE/OFL02/CALIB/CES',
                                    runType = 'Las_REF',
                                    tag=tag,
                                    verbose=False) )

# Workers that perform the laser data analysis
if doDirect:
    # Global correction
    processors.append( getGlobalShiftsDirect(siglim=2.0, n_iter=3, verbose=True) )
    # Fibre correction
    processors.append( getFiberShiftsDirect(siglim=1.5, n_iter=3, verbose=True) )
    doEBscale=True
    if doEBscale:
        # And finally the corrected PMT shifts, (stored in event.data['deviation'])
        processors.append( getPMTShiftsDirect() )
        processors.append( scaleEB() ) 

else:
    # Global correction
    processors.append( getGlobalShiftsCombined(siglim=2.0, n_iter=3, verbose=True) )
    # Fibre correction
    processors.append( getFiberShiftsCombined(siglim=2.0, n_iter=3, verbose=False) )  
    # And finally the globally corrected PMT shifts, (stored in event.data['deviation'])
    processors.append( getPMTShiftsDirect(usePisa=False) )

doOpticsCorrectionPlots = True
if doOpticsCorrectionPlots:
    processors.append( do_global_plot(doEps = plotEps) ) # Plot global correction
    processors.append( do_fiber_plot(doEps = plotEps) ) # Plot fibre correction

# Averages over the key parameter over the set uf runs in Use 
#processors.append( DoAverageValues(key='deviation', verbose=False, removeOutliers=False) )
# Plot difference between the response of the two PMTs reading the same cell
#processors.append( do_pmts_combined_deviation(doEps=True, runNumber=346983) )

# Plots average response of all PMTs of a given cell type as a function of time
doCellAveragePlot = True
if doCellAveragePlot:
    cells =['A9','A10','A12','E1','E2','E3','E4']
    processors.append(do_AverageCells_GausWidth(f =(lambda event: -50000. if (event.data.has_key('deviation')) else event.data.has_key('Pisa_deviation') ), cells=cells, label='',doPdfEps=True, doGaussianWidthplot=True, verbose=True, meanwidth=2))
    

# Plots average response of all PMTs and gaussian width evolution of the fit of a given cell type as a function of time
doLayerAveragePlot = True
if doLayerAveragePlot:
    processors.append(do_AverageLayers_GausWidth(f=(lambda event: -50000. if (event.data.has_key('deviation')) else event.data.has_key('Pisa_deviation') ),label="",doPdfEps=True , verbose=False, splitBarrels=True, doGaussianWidthplot=True, meanwidth=2, Fit="chi2"))

# TGraphs with cells deviation per module and with channel deviation
#cells =['A9','E3','D6']
#processors.append(cellEvolution_perModule_combined(cells=cells, verbose=False))
#processors.append(channelEvolution_combined(cells=cells,verbose=False)) #accepts cells='all' as argument


# Produces bad channel list (LaserBch.txt)
#processors.append( getBadChannels() )
# Reads the Beta & HVnom values from a file and adds it to the PMT region data 
#processors.append( FillBetaHVNom() )


# The last steps are describing the plot production (default plots are .png)
#
# At each level, you could produce plots for few parts or for all the TileCal
#
# Below are some examples (set to True what you want to try)

doPMTPlots   = True
doHVPlot     = False
doChanPlot   = False
doITC        = True
doProblems   = False
doPlotNew    = True

if region == None:
    region=''

if doPMTPlots:
    if region == '':
        processors.append( do_pmts_plot_2gains(limit=1., ymin=-10., ymax=+5., doEps=plotEps))  # All modules
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
    processors.append( set_chan_plot_itc() )

if doProblems:
    badProblems = ['ADC masked (unspecified)', 'ADC dead', "No data", "Very large HF noise", "Stuck bit", "Severe stuck bit",
                   'Severe data corruption', 'Channel masked (unspecified)','No PMT connected', 'Wrong HV']
    # badProblems = ['Bad laser calibration','No laser calibration']
    processors.append( set_chan_plot_problems(problems=badProblems, doEps = plotEps))

if doChanPlot:
    if region=='' or region.find('LBA')!=-1:
        processors.append( set_chan_plot(limit=1, part=LBA, mod=4, chan=44, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBA, mod=34, chan=13, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBA, mod=37, chan=19, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBA, mod=41, chan=32, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBA, mod=42, chan=12, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBA, mod=35, chan=3, doEps = plotEps)) # R11187 pmt
        processors.append( set_chan_plot(limit=1, part=LBA, mod=37, chan=1, doEps = plotEps)) # R11187 pmt

    if region=='' or region.find('LBC')!=-1:
        processors.append( set_chan_plot(limit=1, part=LBC, mod=18, chan=12, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=20, chan=28, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=20, chan=39, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=20, chan=44, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=27, chan=45, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=28, chan=4,  doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=28, chan=35, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=29, chan=26, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=56, chan=10, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=59, chan=33, doEps = plotEps))
        
#        for chan in range(48):
#            processors.append( set_chan_plot(limit=1, part=LBC, mod= 6, chan=chan, doEps = plotEps))
#            processors.append( set_chan_plot(limit=1, part=LBC, mod=17, chan=chan, doEps = plotEps))
#        for chan in [1, 3, 5, 7, 9,11,13,15,17,19,21,23,25,27,29,33,35,37,39,41,45,47]:
#            processors.append( set_chan_plot(limit=1, part=LBC, mod=17, chan=chan, doEps = plotEps))

    if region=='' or region.find('EBA')!=-1:
        processors.append( set_chan_plot(limit=1, part=EBA, mod= 3, chan=7,  doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBA, mod=34, chan=8,  doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBA, mod=49, chan=00, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBA, mod=49, chan=31, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBA, mod=61, chan=10, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBA, mod=61, chan=16, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBA, mod=63, chan=15, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBA, mod=53, chan=1,  doEps = plotEps)) # R11187 pmt

    if region=='' or region.find('EBC')!=-1:
        processors.append( set_chan_plot(limit=1, part=EBC, mod=5,  chan=4,  doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=12, chan=36, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=18, chan=4,  doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=23, chan=31, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=31, chan=41, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=46, chan=7,  doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=55, chan=6,  doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=56, chan=41, doEps = plotEps))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=64, chan=31, doEps = plotEps))
        
#        processors.append( set_chan_plot(limit=1, part=EBC, mod=57, chan=37, doEps = plotEps))
#        for chan in [1,3,5,7,9,11,13,15,17,21,23,32,35,36,37,40]:
#        for chan in [0,2,4,6,8,10,12,14,16,20,22,30,31,38,39,41]:
#            processors.append( set_chan_plot(limit=1, part=EBC, mod=23, chan=chan, doEps = plotEps))
#            processors.append( set_chan_plot(limit=1, part=EBC, mod=24, chan=chan, doEps = plotEps))
            
        pass

if doPlotNew:
    processors.append( do_chan_plot_new(limit=1., doEps = plotEps))
 
Go(processors,withMBTS=False)
