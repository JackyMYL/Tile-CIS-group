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
                   region=region, TWOInput=twoinput) ]

if os.path.exists('/data/ntuples/las'):
    b = ReadLaser(processingDir='/data/ntuples/las',diode_num_lg=0, 
                  diode_num_hg=0,
                  doPisa=usePisa) #, verbose=True
else:
    b = ReadLaser(diode_num_lg=0, diode_num_hg=0, doPisa=usePisa)

processors.append( b )

processors.append( CleanLaser() )

processors.append( ReadBchFromCool( schema='COOLOFL_TILE/CONDBR2',
                                    folder='/TILE/OFL02/STATUS/ADC',
                                    tag='UPD4',
                                    Fast=True,
                                    storeADCinfo=True ) )


if os.path.isfile("tileSqlite.db"):
    processors.append( ReadCalFromCool( schema='sqlite://;schema=tileSqlite.db;dbname=CONDBR2',
                                        folder='/TILE/OFL02/CALIB/CES',
                                        runType = 'Las_REF',
                                        tag = 'RUN2-HLT-UPD1-01',
                                        verbose=True) )
else:
    processors.append( ReadCalFromCool( schema='COOLOFL_TILE/CONDBR2',
                                        folder='/TILE/OFL02/CALIB/CES',
                                        runType = 'Las_REF',
                                        tag = 'UPD4',
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
    badProblems = ['ADC masked (unspecified)', 'ADC dead', "No data", "Very large HF noise", "Severe stuck bit",
                   'Severe data corruption',
                   'Channel masked (unspecified)','No PMT connected', 'Wrong HV']
    processors.append( set_chan_plot_problems(limit=1, problems=badProblems, doEps = True))

# if region=='' or region.find('LBA')!=-1:
#     processors.append( set_chan_plot(limit=1, part=LBA, mod=  3, chan= 7, doEps = True))  # Larry
#     processors.append( set_chan_plot(limit=1, part=LBA, mod= 21, chan=19, doEps = True))  # Larry
#     processors.append( set_chan_plot(limit=1, part=LBA, mod= 37, chan= 1, doEps = True))  # Larry
#     processors.append( set_chan_plot(limit=1, part=LBA, mod= 48, chan=45, doEps = True))  # Larry
# if region=='' or region.find('LBC')!=-1:
#     processors.append( set_chan_plot(limit=1, part=LBC, mod= 20, chan=42, doEps = True))  # HV pb on July 16th 2012
#     processors.append( set_chan_plot(limit=1, part=LBC, mod= 63, chan=41, doEps = True))  # Unmasked weid beast

# # if region=='' or region.find('LBA')!=-1:
# #     processors.append( set_chan_plot(limit=1, part=LBA, mod=21, chan=19, doEps = True))
# # if region=='' or region.find('LBC')!=-1:
# #     processors.append( set_chan_plot(limit=1, part=LBC, mod=44, chan=34, doEps = True))
# #     processors.append( set_chan_plot(limit=1, part=LBC, mod=59, chan=33, doEps = True)) # Tho's list
# #     processors.append( set_chan_plot(limit=1, part=LBC, mod=63, chan=41, doEps = True)) # Tho's list
# # if region=='' or region.find('EBA')!=-1:
# #     processors.append( set_chan_plot(limit=1, part=EBA, mod= 63, chan=15, doEps = True))  # Unmasked weid beast
# # if region=='' or region.find('EBC')!=-1:
# #     processors.append( set_chan_plot(limit=1, part=EBC, mod= 38, chan= 1, doEps = True))
# #     processors.append( set_chan_plot(limit=1, part=EBC, mod= 63, chan=15, doEps = True))  # Unmasked weid beast

#     processors.append( set_chan_plot(limit=1, part=EBC, mod=  8, chan=35, doEps = True))  # Unmasked weid beast, low gain
#     processors.append( set_chan_plot(limit=1, part=EBC, mod= 38, chan= 1, doEps = True))  # Unmasked weid beast, low gain
#     processors.append( set_chan_plot(limit=1, part=EBC, mod= 40, chan= 0, doEps = True))  # Unmasked weid beast, low gain
#     processors.append( set_chan_plot(limit=1, part=EBC, mod= 62, chan= 0, doEps = True))  # Unmasked weid beast, low gain
#     processors.append( set_chan_plot(limit=1, part=EBC, mod= 53, chan=39, doEps = True))
#     processors.append( set_chan_plot(limit=1, part=EBC, mod= 55, chan=36, doEps = True))
#     processors.append( set_chan_plot(limit=1, part=EBC, mod= 56, chan=36, doEps = True))
#     processors.append( set_chan_plot(limit=1, part=EBC, mod= 63, chan=15, doEps = True))
#     processors.append( set_chan_plot(limit=1, part=EBC, mod= 64, chan=31, doEps = True))
#     processors.append( set_chan_plot(limit=1, part=EBC, mod= 64, chan=32, doEps = True))

# Nazim channels:
# processors.append(set_chan_plot(runType='Las', limit=1, part=EBA, mod=50, chan=13, doEps = True))
# processors.append(set_chan_plot(runType='Las', limit=1, part=EBC, mod=53, chan=13, doEps = True))

if doHVPlot:
    if region=='' or region.find('LBA')!=-1:
        print "We will do problematic HV plot for LBA"
        processors.append( set_chan_plot(limit=1, part=LBA, mod=15, chan=16, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=LBA, mod=17, chan=16, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=LBA, mod=19, chan=02, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=LBA, mod=21, chan=34, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=LBA, mod=23, chan= 3, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=LBA, mod=23, chan=42, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=LBA, mod=33, chan=16, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=LBA, mod=37, chan= 6, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=LBA, mod=43, chan=01, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=LBA, mod=47, chan=02, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=LBA, mod=50, chan=23, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=LBA, mod=51, chan= 9, doEps = True)) # HV pb, Sacha' list
        processors.append( set_chan_plot(limit=1, part=LBA, mod=53, chan=16, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=LBA, mod=59, chan=12, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=LBA, mod=61, chan=13, doEps = True)) # HV pb

    if region=='' or region.find('LBC')!=-1:
        print "We will do problematic HV plot for LBC"
        processors.append( set_chan_plot(limit=1, part=LBC, mod= 3, chan=41, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=LBC, mod= 4, chan=20, doEps = True)) # HV pb, Tho's list
        processors.append( set_chan_plot(limit=1, part=LBC, mod=23, chan=13, doEps = True)) # Henric adds,  HV pb
        processors.append( set_chan_plot(limit=1, part=LBC, mod=27, chan=17, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=LBC, mod=28, chan= 7, doEps = True)) # HV pb, Henric adds,
        processors.append( set_chan_plot(limit=1, part=LBC, mod=42, chan=40, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=LBC, mod=43, chan=36, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=LBC, mod=44, chan=18, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=LBC, mod=44, chan=38, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=LBC, mod=45, chan=29, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=LBC, mod=45, chan=47, doEps = True)) # Henric adds, HV pb
        processors.append( set_chan_plot(limit=1, part=LBC, mod=46, chan=41, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=LBC, mod=57, chan=13, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=LBC, mod=58, chan=21, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=LBC, mod=59, chan= 4, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=LBC, mod=60, chan=16, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=LBC, mod=62, chan=23, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=LBC, mod=62, chan=39, doEps = True)) # HV pb

    if region=='' or region.find('EBA')!=-1:
        processors.append( set_chan_plot(limit=1, part=EBA, mod= 7, chan=39, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=EBA, mod=17, chan= 8, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=EBA, mod=35, chan= 5, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=EBA, mod=38, chan=10, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=EBA, mod=40, chan=30, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=EBA, mod=61, chan=11, doEps = True)) # HV pb

    if region=='' or region.find('EBC')!=-1:
        processors.append( set_chan_plot(limit=1, part=EBC, mod=20, chan= 0, doEps = True)) # HV pb but MBTS
        processors.append( set_chan_plot(limit=1, part=EBC, mod=30, chan=13, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=EBC, mod=31, chan=36, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=EBC, mod=36, chan= 5, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=EBC, mod=40, chan=13, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=EBC, mod=51, chan=13, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=EBC, mod=51, chan=14, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=EBC, mod=53, chan=21, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=EBC, mod=56, chan=36, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=EBC, mod=60, chan= 6, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=EBC, mod=60, chan=10, doEps = True)) # Why marked?
        processors.append( set_chan_plot(limit=1, part=EBC, mod=61, chan=17, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=EBC, mod=61, chan=22, doEps = True)) # HV pb
        processors.append( set_chan_plot(limit=1, part=EBC, mod=64, chan=32, doEps = True)) # Henric adds, HV pb

#
# Go for it!!!
#

# Sacha & Tho channels:

#Emmanuelle's channels

for pmt in range(1,48):
    processors.append( set_chan_plot(limit=1, part=LBA, mod=17, chan=pmt, doEps = True))
    processors.append( set_chan_plot(limit=1, part=LBC, mod=17, chan=pmt, doEps = True))
     

if doChanPlot:
    if region=='' or region.find('LBA')!=-1:

        processors.append( set_chan_plot(limit=1, part=LBA, mod= 4, chan=44, doEps = True))
        processors.append( set_chan_plot(limit=1, part=LBA, mod=16, chan=33, doEps = True))
        processors.append( set_chan_plot(limit=1, part=LBA, mod=21, chan=19, doEps = True))
        processors.append( set_chan_plot(limit=1, part=LBA, mod=34, chan= 2, doEps = True))
        processors.append( set_chan_plot(limit=1, part=LBA, mod=37, chan=19, doEps = True))
        processors.append( set_chan_plot(limit=1, part=LBA, mod=38, chan=15, doEps = True))
        processors.append( set_chan_plot(limit=1, part=LBA, mod=53, chan=33, doEps = True))

    if region=='' or region.find('LBC')!=-1:

        processors.append( set_chan_plot(limit=1, part=LBC, mod=14, chan= 1, doEps = True))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=24, chan= 3, doEps = True))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=24, chan= 4, doEps = True))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=24, chan= 5, doEps = True))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=26, chan=38, doEps = True))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=55, chan=27, doEps = True))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=57, chan= 6, doEps = True))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=57, chan= 7, doEps = True))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=57, chan= 8, doEps = True))
        processors.append( set_chan_plot(limit=1, part=LBC, mod=59, chan=33, doEps = True))

    if region=='' or region.find('EBA')!=-1:

        processors.append( set_chan_plot(limit=1, part=EBA, mod=63, chan=15, doEps = True))

    if region=='' or region.find('EBC')!=-1:

        processors.append( set_chan_plot(limit=1, part=EBC, mod= 5, chan=20, doEps = True))
        processors.append( set_chan_plot(limit=1, part=EBC, mod= 9, chan=40, doEps = True))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=13, chan=37, doEps = True))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=18, chan= 4, doEps = True))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=20, chan=10, doEps = True))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=29, chan=15, doEps = True))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=30, chan=22, doEps = True))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=43, chan= 4, doEps = True))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=58, chan=21, doEps = True))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=58, chan=22, doEps = True))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=58, chan=23, doEps = True))
        processors.append( set_chan_plot(limit=1, part=EBC, mod=63, chan=15, doEps = True))


# All ITC:
#     for part in [EBA, EBC]:
#         for module in range(1,65):
#             if (part==EBA and module==15) or (part==EBC and module==18):
#                 processors.append( set_chan_plot(limit=1, part=part, mod=module, chan=18, doEps = True) ) # E3 or MBTS
#                 processors.append( set_chan_plot(limit=1, part=part, mod=module, chan=19, doEps = True) ) # E4
#             else:
#                 processors.append( set_chan_plot(limit=1, part=part, mod=module, chan= 0, doEps = True) ) # E3 or MBTS
#                 processors.append( set_chan_plot(limit=1, part=part, mod=module, chan= 1, doEps = True) ) # E4

#             processors.append( set_chan_plot(limit=1, part=part, mod=module, chan= 2, doEps = True) ) # D4
#             processors.append( set_chan_plot(limit=1, part=part, mod=module, chan= 3, doEps = True) ) # D4

#             processors.append( set_chan_plot(limit=1, part=part, mod=module, chan= 5, doEps = True) ) # C10
#             processors.append( set_chan_plot(limit=1, part=part, mod=module, chan= 6, doEps = True) ) # C10

#             processors.append( set_chan_plot(limit=1, part=part, mod=module, chan=12, doEps = True) ) # E1
#             processors.append( set_chan_plot(limit=1, part=part, mod=module, chan=13, doEps = True) ) # E2



processors.append( set_chan_plot(limit=1, part=EBC, mod=22, chan=0, doEps = True)) 
processors.append( set_chan_plot(limit=1, part=EBC, mod=22, chan=1, doEps = True)) 

Go(processors,withMBTS=False)

