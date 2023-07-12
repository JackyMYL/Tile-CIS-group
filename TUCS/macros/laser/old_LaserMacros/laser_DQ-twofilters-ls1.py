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
processors = [ ]

# processors.append( Use(runs, run2=enddate, filter=filt_pos, runType='Las',
#                        region=region, TWOInput=twoinput)  )

processors.append( Use('2013-03-26',runType='Las',region='LBC_m37,LBC_m38,LBC_m60',TWOInput=True))
processors.append( Use('2013-04-02',runType='Las',region='LBA_m37,LBA_m61',TWOInput=True))
processors.append( Use('2013-04-04',runType='Las',region='LBA_m60',TWOInput=True))
processors.append( Use('2013-04-10',runType='Las',region='LBA_m22,LBA_m62',TWOInput=True))
processors.append( Use('2013-04-11',runType='Las',region='LBA_m11,LBA_m12,LBA_m13,LBA_m14,LBA_m21,LBA_m36,LBA_m38,LBA_m59',TWOInput=True))
processors.append( Use('2013-04-15',runType='Las',region='LBA_m19',TWOInput=True))
processors.append( Use('2013-04-17',runType='Las',region='LBA_m04,LBA_m35',TWOInput=True))
processors.append( Use('2013-04-18',runType='Las',region='LBA_m03,LBA_m08,LBA_m18,LBC_m18',TWOInput=True))
processors.append( Use('2013-04-24',runType='Las',region='LBA_m05,LBA_m16,LBA_m30',TWOInput=True))
processors.append( Use('2013-04-26',runType='Las',region='LBA_m29',TWOInput=True))
processors.append( Use('2013-05-08',runType='Las',region='LBA_m17,LBA_m31,LBA_m50',TWOInput=True))
processors.append( Use('2013-05-10',runType='Las',region='LBA_m32',TWOInput=True))
processors.append( Use('2013-05-14',runType='Las',region='LBA_m33',TWOInput=True))
processors.append( Use('2013-05-15',runType='Las',region='LBA_m51,LBA_m52',TWOInput=True))
processors.append( Use('2013-05-16',runType='Las',region='LBA_m46',TWOInput=True))
processors.append( Use('2013-05-17',runType='Las',region='LBA_m45',TWOInput=True))
processors.append( Use('2013-05-18',runType='Las',region='LBA_m34',TWOInput=True))
processors.append( Use('2013-05-22',runType='Las',region='LBA_m25,LBA_m44',TWOInput=True))
processors.append( Use('2013-05-28',runType='Las',region='LBA_m02,LBA_m43,LBA_m53,LBC_m41',TWOInput=True))
processors.append( Use('2013-05-30',runType='Las',region='LBC_m42',TWOInput=True))
processors.append( Use('2013-05-31',runType='Las',region='LBA_m01,LBA_m54',TWOInput=True))
processors.append( Use('2013-06-03',runType='Las',region='LBC_m08,LBC_m43',TWOInput=True))
processors.append( Use('2013-06-05',runType='Las',region='LBC_m44',TWOInput=True))
processors.append( Use('2013-06-07',runType='Las',region='LBC_m09,LBC_m10,LBC_m22',TWOInput=True))
processors.append( Use('2013-06-10',runType='Las',region='LBC_m11,LBC_m23,LBC_m45',TWOInput=True))
processors.append( Use('2013-06-11',runType='Las',region='LBC_m46',TWOInput=True))
processors.append( Use('2013-06-12',runType='Las',region='LBC_m21,LBC_m47',TWOInput=True))
processors.append( Use('2013-06-13',runType='Las',region='LBC_m12,LBC_m48',TWOInput=True))
processors.append( Use('2013-06-16',runType='Las',region='LBC_m49',TWOInput=True))
processors.append( Use('2013-06-17',runType='Las',region='LBC_m13,LBC_m25,LBC_m50',TWOInput=True))
processors.append( Use('2013-06-18',runType='Las',region='LBC_m14',TWOInput=True))
processors.append( Use('2013-06-19',runType='Las',region='LBC_m29',TWOInput=True))
processors.append( Use('2013-06-20',runType='Las',region='LBC_m24,LBC_m51,LBC_m52',TWOInput=True))
processors.append( Use('2013-06-21',runType='Las',region='LBC_m28',TWOInput=True))
processors.append( Use('2013-06-24',runType='Las',region='LBC_m53',TWOInput=True))
processors.append( Use('2013-06-25',runType='Las',region='LBC_m54',TWOInput=True))
processors.append( Use('2013-06-26',runType='Las',region='LBC_m16',TWOInput=True))
processors.append( Use('2013-06-28',runType='Las',region='LBA_m15,LBC_m15',TWOInput=True))
processors.append( Use('2013-07-02',runType='Las',region='LBC_m17,LBC_m19',TWOInput=True))
processors.append( Use('2013-07-03',runType='Las',region='LBC_m20,LBC_m30',TWOInput=True))
processors.append( Use('2013-07-04',runType='Las',region='LBC_m31',TWOInput=True))
processors.append( Use('2013-07-05',runType='Las',region='LBC_m55',TWOInput=True))
processors.append( Use('2013-07-09',runType='Las',region='LBC_m03,LBC_m32',TWOInput=True))
processors.append( Use('2013-07-10',runType='Las',region='LBC_m33',TWOInput=True))
processors.append( Use('2013-07-15',runType='Las',region='LBC_m02',TWOInput=True))
processors.append( Use('2013-07-16',runType='Las',region='LBC_m01,LBC_m34',TWOInput=True))
processors.append( Use('2013-07-17',runType='Las',region='LBC_m04,LBC_m35,LBC_m64',TWOInput=True))
processors.append( Use('2013-07-18',runType='Las',region='LBC_m61',TWOInput=True))
processors.append( Use('2013-07-19',runType='Las',region='LBC_m36',TWOInput=True))
processors.append( Use('2013-07-22',runType='Las',region='LBC_m59',TWOInput=True))
processors.append( Use('2013-07-23',runType='Las',region='LBC_m62',TWOInput=True))
processors.append( Use('2013-07-24',runType='Las',region='LBC_m06,LBC_m56',TWOInput=True))
processors.append( Use('2013-07-25',runType='Las',region='LBC_m63',TWOInput=True))
processors.append( Use('2013-07-26',runType='Las',region='LBC_m05',TWOInput=True))
processors.append( Use('2013-07-29',runType='Las',region='LBC_m26',TWOInput=True))
processors.append( Use('2013-07-30',runType='Las',region='LBA_m64,LBC_m27',TWOInput=True))
processors.append( Use('2013-08-01',runType='Las',region='LBA_m49',TWOInput=True))
processors.append( Use('2013-08-05',runType='Las',region='LBA_m20',TWOInput=True))
processors.append( Use('2013-08-06',runType='Las',region='LBA_m24,LBC_m07',TWOInput=True))
processors.append( Use('2013-08-08',runType='Las',region='LBA_m48',TWOInput=True))
processors.append( Use('2013-08-09',runType='Las',region='LBA_m47',TWOInput=True))
processors.append( Use('2013-08-12',runType='Las',region='LBA_m23',TWOInput=True))
processors.append( Use('2013-08-14',runType='Las',region='LBA_m09',TWOInput=True))
processors.append( Use('2013-08-15',runType='Las',region='EBA_m20',TWOInput=True))
processors.append( Use('2013-08-16',runType='Las',region='EBA_m22',TWOInput=True))
processors.append( Use('2013-08-19',runType='Las',region='LBA_m10',TWOInput=True))
processors.append( Use('2013-08-20',runType='Las',region='EBA_m21',TWOInput=True))
processors.append( Use('2013-08-21',runType='Las',region='EBA_m11,EBA_m18',TWOInput=True))
processors.append( Use('2013-08-26',runType='Las',region='EBA_m14',TWOInput=True))
processors.append( Use('2013-08-27',runType='Las',region='EBA_m19',TWOInput=True))
processors.append( Use('2013-08-28',runType='Las',region='EBA_m10,EBA_m16',TWOInput=True))
processors.append( Use('2013-08-30',runType='Las',region='EBA_m09,EBA_m17',TWOInput=True))
processors.append( Use('2013-09-09',runType='Las',region='EBA_m62',TWOInput=True))
processors.append( Use('2013-09-10',runType='Las',region='EBA_m64',TWOInput=True))
processors.append( Use('2013-09-11',runType='Las',region='EBA_m01',TWOInput=True))
processors.append( Use('2013-09-13',runType='Las',region='EBA_m02',TWOInput=True))
processors.append( Use('2013-09-18',runType='Las',region='EBA_m37',TWOInput=True))
processors.append( Use('2013-09-20',runType='Las',region='EBA_m34,EBA_m49',TWOInput=True))
processors.append( Use('2013-09-24',runType='Las',region='EBA_m59',TWOInput=True))
processors.append( Use('2013-09-25',runType='Las',region='EBA_m39',TWOInput=True))
processors.append( Use('2013-09-26',runType='Las',region='EBA_m36,EBA_m38,EBA_m60',TWOInput=True))
processors.append( Use('2013-10-01',runType='Las',region='EBC_m53',TWOInput=True))
processors.append( Use('2013-10-08',runType='Las',region='EBA_m35',TWOInput=True))
processors.append( Use('2013-10-09',runType='Las',region='EBA_m61',TWOInput=True))
processors.append( Use('2013-10-10',runType='Las',region='EBA_m15',TWOInput=True))
processors.append( Use('2013-10-11',runType='Las',region='EBA_m33',TWOInput=True))
processors.append( Use('2013-10-15',runType='Las',region='EBA_m13,EBA_m32',TWOInput=True))
processors.append( Use('2013-10-16',runType='Las',region='EBA_m12',TWOInput=True))
processors.append( Use('2013-10-17',runType='Las',region='EBA_m31',TWOInput=True))
processors.append( Use('2013-10-24',runType='Las',region='EBA_m03',TWOInput=True))
processors.append( Use('2013-10-25',runType='Las',region='EBA_m30',TWOInput=True))
processors.append( Use('2013-10-29',runType='Las',region='EBA_m05,EBA_m23',TWOInput=True))
processors.append( Use('2013-10-31',runType='Las',region='EBA_m04,EBC_m52',TWOInput=True))
processors.append( Use('2013-11-02',runType='Las',region='EBA_m29',TWOInput=True))
processors.append( Use('2013-11-04',runType='Las',region='EBC_m44',TWOInput=True))
processors.append( Use('2013-11-08',runType='Las',region='LBA_m07,EBA_m28',TWOInput=True))
processors.append( Use('2013-11-11',runType='Las',region='LBA_m06,EBC_m45',TWOInput=True))
processors.append( Use('2013-11-12',runType='Las',region='EBA_m27',TWOInput=True))
processors.append( Use('2013-11-16',runType='Las',region='LBA_m28',TWOInput=True))
processors.append( Use('2013-11-18',runType='Las',region='LBA_m27,EBA_m06,EBA_m07',TWOInput=True))
processors.append( Use('2013-11-21',runType='Las',region='EBA_m08,EBA_m24,EBC_m43',TWOInput=True))
processors.append( Use('2013-11-22',runType='Las',region='EBA_m25',TWOInput=True))
processors.append( Use('2013-11-25',runType='Las',region='EBA_m26',TWOInput=True))
processors.append( Use('2013-11-26',runType='Las',region='LBA_m26,EBC_m54',TWOInput=True))
processors.append( Use('2013-11-27',runType='Las',region='EBA_m54',TWOInput=True))
processors.append( Use('2013-11-28',runType='Las',region='LBA_m63,EBA_m63',TWOInput=True))
processors.append( Use('2013-11-30',runType='Las',region='EBA_m43',TWOInput=True))
processors.append( Use('2013-12-02',runType='Las',region='EBA_m46,EBA_m52,EBA_m53',TWOInput=True))
processors.append( Use('2013-12-03',runType='Las',region='EBA_m47',TWOInput=True))
processors.append( Use('2013-12-05',runType='Las',region='EBA_m48,EBA_m51',TWOInput=True))
processors.append( Use('2013-12-06',runType='Las',region='EBA_m45',TWOInput=True))
processors.append( Use('2013-12-10',runType='Las',region='EBA_m44,EBA_m50',TWOInput=True))
processors.append( Use('2014-01-13',runType='Las',region='EBC_m09',TWOInput=True))
processors.append( Use('2014-01-14',runType='Las',region='EBC_m17,EBC_m48',TWOInput=True))
processors.append( Use('2014-01-15',runType='Las',region='EBC_m12,EBC_m19,EBC_m49',TWOInput=True))
processors.append( Use('2014-01-16',runType='Las',region='EBC_m13,EBC_m50',TWOInput=True))
processors.append( Use('2014-01-17',runType='Las',region='EBC_m14,EBC_m18,EBC_m20,EBC_m51',TWOInput=True))
processors.append( Use('2014-01-21',runType='Las',region='EBC_m24,EBC_m27,EBC_m47',TWOInput=True))
processors.append( Use('2014-01-22',runType='Las',region='EBC_m15,EBC_m46',TWOInput=True))
processors.append( Use('2014-01-23',runType='Las',region='EBC_m04,EBC_m16,EBC_m28',TWOInput=True))
processors.append( Use('2014-01-24',runType='Las',region='EBC_m10,EBC_m55',TWOInput=True))
processors.append( Use('2014-01-28',runType='Las',region='EBC_m05,EBC_m29,EBC_m56',TWOInput=True))
processors.append( Use('2014-01-29',runType='Las',region='EBC_m30',TWOInput=True))
processors.append( Use('2014-02-04',runType='Las',region='LBC_m40,EBC_m03,EBC_m06,EBC_m41',TWOInput=True))
processors.append( Use('2014-02-06',runType='Las',region='EBC_m07,EBC_m25',TWOInput=True))
processors.append( Use('2014-02-07',runType='Las',region='EBC_m26,LBC_m57',TWOInput=True))
processors.append( Use('2014-02-11',runType='Las',region='EBC_m08,EBC_m42',TWOInput=True))
processors.append( Use('2014-02-13',runType='Las',region='EBC_m11,EBC_m31',TWOInput=True))
processors.append( Use('2014-02-17',runType='Las',region='EBC_m01',TWOInput=True))
processors.append( Use('2014-02-19',runType='Las',region='EBC_m02,EBC_m32',TWOInput=True))
processors.append( Use('2014-02-21',runType='Las',region='EBC_m33',TWOInput=True))
processors.append( Use('2014-02-24',runType='Las',region='EBC_m34',TWOInput=True))
processors.append( Use('2014-02-25',runType='Las',region='EBC_m63',TWOInput=True))
processors.append( Use('2014-02-26',runType='Las',region='EBC_m35,EBC_m62',TWOInput=True))
processors.append( Use('2014-02-28',runType='Las',region='EBC_m36,EBC_m60',TWOInput=True))
processors.append( Use('2014-03-04',runType='Las',region='EBC_m64',TWOInput=True))
processors.append( Use('2014-03-05',runType='Las',region='EBC_m37',TWOInput=True))
processors.append( Use('2014-03-06',runType='Las',region='EBC_m61',TWOInput=True))
processors.append( Use('2014-03-10',runType='Las',region='EBC_m59',TWOInput=True))
processors.append( Use('2014-03-12',runType='Las',region='EBC_m38',TWOInput=True))
processors.append( Use('2014-03-13',runType='Las',region='EBC_m40',TWOInput=True))
processors.append( Use('2014-03-17',runType='Las',region='EBC_m57',TWOInput=True))
processors.append( Use('2014-03-25',runType='Las',region='EBC_m58',TWOInput=True))
processors.append( Use('2014-03-28',runType='Las',region='EBC_m39',TWOInput=True))
processors.append( Use('2014-06-14',runType='Las',region='LBC_m39,LBC_m58',TWOInput=True))
processors.append( Use('2014-07-03',runType='Las',region='EBC_m21',TWOInput=True))
processors.append( Use('2014-07-04',runType='Las',region='EBC_m22',TWOInput=True))
processors.append( Use('2014-07-10',runType='Las',region='EBC_m23',TWOInput=True))
processors.append( Use('2014-07-18',runType='Las',region='LBA_m42,EBA_m42',TWOInput=True))
processors.append( Use('2014-07-23',runType='Las',region='EBA_m55',TWOInput=True))
processors.append( Use('2014-08-01',runType='Las',region='LBA_m55',TWOInput=True))
processors.append( Use('2014-08-13',runType='Las',region='LBC_m57',TWOInput=True))
processors.append( Use('2014-08-15',runType='Las',region='LBA_m41,LBA_m57',TWOInput=True))
processors.append( Use('2014-08-16',runType='Las',region='LBA_m40',TWOInput=True))
processors.append( Use('2014-08-17',runType='Las',region='LBA_m39,LBA_m56,LBA_m58',TWOInput=True))
processors.append( Use('2014-08-28',runType='Las',region='EBA_m58',TWOInput=True))
processors.append( Use('2014-08-30',runType='Las',region='EBA_m40,EBA_m41,EBA_m56,EBA_m57',TWOInput=True))





if os.path.exists('/data/ntuples/las'):
    b = ReadLaser(processingDir='/data/ntuples/las',diode_num_lg=0, diode_num_hg=0, doPisa=usePisa) #, verbose=True
else:
    b = ReadLaser(diode_num_lg=0, diode_num_hg=0, doPisa=usePisa)

processors.append( b )

processors.append( CleanLaser() )

processors.append( ReadBchFromCool( schema='COOLOFL_TILE/CONDBR2',
                                    folder='/TILE/OFL02/STATUS/ADC',
                                    tag='TileOfl02StatusAdc-RUN2-UPD4-08',
                                    Fast=True,
                                    storeADCinfo=True ) )

processors.append( ReadCalFromCool( schema='sqlite://;schema=tileSqlite.db;dbname=COMP200',
                                    folder='/TILE/OFL02/CALIB/CES',
                                    runType = 'Las_REF',
                                    tag = 'TileOfl02CalibCes-HLT-UPD1-01',
                                    #tag = 'RUN2-HLT-UPD1-01',
                                    verbose=True) )

# processors.append( ReadCalFromCool( schema='COOLOFL_TILE/CONDBR2',
#                                     folder='/TILE/OFL02/CALIB/CES',
#                                     runType = 'Las_REF',
#                                     tag = 'UPD4',
#                                     verbose=True) )

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

processors.append( getBadChannels() )
processors.append( FillBetaHVNom() )

# The last steps are describing the plot production (default plots are .png)
#
# At each level, you could produce plots for few parts
# or for all the TileCal
#
# Below are some examples (uncomment what you want to try)

# processors.append( Print(region='LBA_m17_c26') )

doPMTPlots   = True
doHVPlot     = False
doChanPlot   = True
doITC        = False
doProblems   = True

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
    badProblems = ['ADC masked (unspecified)', 'ADC dead', 'No data', 
                   'Very large HF noise', 'Severe stuck bit', 'Severe data corruption',
                   'Channel masked (unspecified)','No PMT connected', 'Wrong HV']
    processors.append( set_chan_plot_problems(limit=1, problems=badProblems, doEps = True))



#processors.append( set_chan_plot(limit=1, part=EBC, mod=22, chan=0, doEps = True)) 
#processors.append( set_chan_plot(limit=1, part=EBC, mod=22, chan=1, doEps = True)) 

processors.append( set_chan_plot(limit=1, part=EBC, mod=5, chan=4, doEps = True)) 
processors.append( set_chan_plot(limit=1, part=EBC, mod=5, chan=20, doEps = True)) 
processors.append( set_chan_plot(limit=1, part=EBC, mod=11, chan=31, doEps = True)) 
processors.append( set_chan_plot(limit=1, part=EBC, mod=12, chan=36, doEps = True)) 
processors.append( set_chan_plot(limit=1, part=EBC, mod=18, chan=4, doEps = True)) 
processors.append( set_chan_plot(limit=1, part=EBC, mod=21, chan=36, doEps = True)) 
processors.append( set_chan_plot(limit=1, part=EBC, mod=57, chan=37, doEps = True)) 
processors.append( set_chan_plot(limit=1, part=EBC, mod=64, chan=31, doEps = True)) 

Go(processors,withMBTS=False)

