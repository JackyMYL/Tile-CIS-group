#!/usr/bin/env python

# TUCS common
import os, re
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

import _NoiseCommon
from datetime import datetime, timedelta

# handle arguments
argparser = _NoiseCommon.common_noise_arguments('Produce new pedestal time evolution data')

# handle arguments
argparser.add_argument('--date', required=False, default='', type=str, help='End date of period, empty means today', dest='date')
argparser.add_argument('--time_span', required=False, default='30', type=str, help='Number of days in period', dest='time_span')
argparser.add_argument('--min_events', required=False, default=0, type=int, help='Minimum number of events in pedestal run', dest='minEvents')
argparser.add_argument('--plot_logy', required=False, default=False, help='Use log scale for the main plot', action='store_true', dest='plotLogY')
argparser.add_argument('--plot_runnumber', required=False, help='Use run numbers on X-axis', action='store_true', dest='plotRunNumber')
argparser.add_argument('--date_format', required=False, default='%y-%m-%d', type=str, help='Format of dates', dest='dateFormat')
argparser.add_argument('--plot_bad_channels', required=False, default=True, help='Plot bad channels', action='store_true', dest='plotBadChannels')

piov_grp = argparser.add_mutually_exclusive_group(required=False)
piov_grp.add_argument('--show_iov_start', required=False, help='Show IOV starts in plots', action='store_true', dest='showIOVStart')
piov_grp.add_argument('--do_not_show_iov_start', required=False, help='Do not show IOV starts in plots', action='store_false', dest='showIOVStart')
argparser.set_defaults(showIOVStart=True)

bc_grp = argparser.add_mutually_exclusive_group(required=False)
bc_grp.add_argument('--exclude_bad_channels', action='store_true', help='Exclude bad channels', dest='excludeBadChannels')
bc_grp.add_argument('--include_bad_channels', action='store_false', help='Include bad channels', dest='excludeBadChannels')
argparser.set_defaults(excludeBadChannels=True)

pn_grp = argparser.add_mutually_exclusive_group(required=False)
pn_grp.add_argument('--plot_noise', action='store_true', help='Plot HF and LF noise', dest='plotNoise')
pn_grp.add_argument('--do_not_plot_noise', action='store_false', help='Plot HF and LF noise', dest='plotNoise')
argparser.set_defaults(plotNoise=True)

sai_grp = argparser.add_mutually_exclusive_group(required=False)
sai_grp.add_argument('--save_adc_details', action='store_true', help='Save ADC details', dest='saveADCDetails')
sai_grp.add_argument('--do_not_save_adc_details', action='store_false', help='Do not plot ADC details', dest='saveADCDetails')
argparser.set_defaults(saveADCDetails=True)

pai_grp = argparser.add_mutually_exclusive_group(required=False)
pai_grp.add_argument('--plot_adc_details', action='store_true', help='Plot ADC details', dest='plotADCDetails')
pai_grp.add_argument('--do_not_plot_adc_details', action='store_false', help='Do not plot ADC details', dest='plotADCDetails')
argparser.set_defaults(plotADCDetails=False)

argparser.add_argument('--plot_prefix', required=False, default='Pedestal', type=str, help='File name prefix', dest='plotPrefix')

argparser.add_argument('--ped_thresholds', nargs=3, type=float, default=[0.5, 3, 10], required=False, help='Pedestal thresholds', dest='ped_thresholds')
argparser.add_argument('--hfn_thresholds', nargs=3, type=float, default=[0.10, 0.3, 0.5], required=False, help='HF noise thresholds', dest='hfn_thresholds')
argparser.add_argument('--lfn_thresholds', nargs=3, type=float, default=[0.10, 0.3, 0.5], required=False, help='LF noise thresholds', dest='lfn_thresholds')

args = argparser.parse_args()

# Determine directories
outputDirectory = _NoiseCommon.determine_output_directory(args)
plot_directory = _NoiseCommon.determine_plot_directory(args)

# Determine dates
date_diff = timedelta(days=int(args.time_span))
end_date = datetime.today() if not args.date else datetime.strptime(args.date, '%Y-%m-%d')
start_date = end_date - date_diff
start_date_str = datetime.strftime(start_date, '%Y-%m-%d')
end_date_str = datetime.strftime(end_date, '%Y-%m-%d')

# Get list of runs
runs = _NoiseCommon.get_runs_in_period(start_date, end_date, args.minEvents)

# determine root file name
root_file_name = None
if not args.outputRoot:
    root_file_name = os.path.join(outputDirectory, 'PedestalTimeEvolution_%s_%s.root' % (start_date_str, end_date_str))
else:
    root_file_name = os.path.join(outputDirectory, args.outputRoot)

output = _NoiseCommon.NoiseOutput('', root_file_name, plot_directory)
output.print_log('Start date: %s end date: %s' % (start_date_str, end_date_str))
output.print_log('Output ROOT file : %s' % (root_file_name))
output.print_log('Run list : %s' % (str(runs)))
output.print_log('Pedestal thresholds: %s' % str(args.ped_thresholds))
output.print_log('HF noise thresholds: %s' % str(args.hfn_thresholds))
output.print_log('LF noise thresholds: %s' % str(args.lfn_thresholds))

plot_noise = args.plotNoise

# Setup workers
selected_region = ''

noise_cmp = 'relative' if args.noiseComparisonModeRelative else 'absolute'

thresholdColors = [400 + 1, 800, 632]

processList = [Use(run=runs, runType='Ped', type='physical', region=selected_region, verbose=args.verbose, keepOnlyActive=False),
               ReadPedestalFile(output=output, minEvents=args.minEvents),
               ReadDigiNoiseDB(runType='Ped', useSqlite=args.dbUseSqlite, dbConn=args.dbConn, dbFile=args.dbSqliteFile,
                               load_autocr=False, folderTag=args.dbFolderTag, readIOVs=args.showIOVStart)]

if args.excludeBadChannels or args.plotBadChannels:
    output.print_log("Use bad channel schema %s with tag %s." % (args.badChannelSchema, args.badChannelTag))
    processList.append(ReadBadChFromCool(schema=args.badChannelSchema, tag=args.badChannelTag, Fast=False, storeADCinfo=False))

# PatchBadValues - Does not work with multiple runs
#if args.patchBadValues:
#    output.print_log("Patch bad values by checking noise attribute '%s'" % args.badChannelAttribute) 
#    processList.append(PatchBadValues(runType='Ped', type='readout', standard_p=args.badChannelAttribute))

processList.extend([PedestalTimeEvolution(output=output, referenceRun=None, compareTo='current_db', plotPrefix=args.plotPrefix,
                                          dataAttribute='ped',
                                          diffThresholds=args.ped_thresholds,
                                          diffThresholdColors=thresholdColors,
                                          showDates=(not args.plotRunNumber), dateFormat=args.dateFormat,
                                          title="Pedestal abs difference", titleY="Number of ADCs",
                                          titleDetails="Pedestal values", titleYDetails="ADC counts",
                                          legendTitle='#Delta pedestal',
                                          plotLogY=args.plotLogY, minY=0.05, maxY=1, 
                                          mode='absolute', sigmaAttribute=None, dbSigmaAttribute=None, 
                                          plotADCDetails=args.plotADCDetails, dbDataAttribute='ped_db', 
                                          splitHiAndLow=False, excludeBadChannels=args.excludeBadChannels,
                                          plotBadChannels=args.plotBadChannels,
                                          plotIOVs=args.showIOVStart,
                                          saveADCDetails=args.saveADCDetails)])

if plot_noise:
    processList.extend([PedestalTimeEvolution(output=output, referenceRun=None, compareTo='current_db', plotPrefix=(args.plotPrefix + 'HFN'),
                                              dataAttribute='hfn',
                                              diffThresholds=args.hfn_thresholds,
                                              diffThresholdColors=thresholdColors,
                                              showDates=(not args.plotRunNumber), dateFormat=args.dateFormat,
                                              title=("HF noise %s difference" % noise_cmp), 
                                              titleY="Number of ADCs",
                                              titleDetails="HF noise", 
                                              titleYDetails="ADC counts",
                                              legendTitle='#Delta rel. HF noise',
                                              plotLogY=args.plotLogY, minY=0.05, maxY=1, 
                                              mode=noise_cmp, sigmaAttribute='', dbSigmaAttribute='hfn_db', 
                                              plotADCDetails=args.plotADCDetails, dbDataAttribute='hfn_db', 
                                              splitHiAndLow=False,
                                              excludeBadChannels=args.excludeBadChannels,
                                              plotBadChannels=args.plotBadChannels,
                                              plotIOVs=args.showIOVStart,
                                              saveADCDetails=args.saveADCDetails),
                        PedestalTimeEvolution(output=output, referenceRun=None, compareTo='current_db', plotPrefix=(args.plotPrefix + 'LFN'),
                                              dataAttribute='lfn',
                                              diffThresholds=args.lfn_thresholds,
                                              diffThresholdColors=thresholdColors,
                                              showDates=(not args.plotRunNumber), dateFormat=args.dateFormat,
                                              title=("LF noise %s difference" % noise_cmp), 
                                              titleY="Number of ADCs",
                                              titleDetails="LF noise", 
                                              titleYDetails="ADC counts",
                                              legendTitle='#Delta rel. LF noise',
                                              plotLogY=args.plotLogY, minY=0.05, maxY=1, 
                                              mode=noise_cmp, sigmaAttribute='', dbSigmaAttribute='lfn_db', 
                                              plotADCDetails=args.plotADCDetails, dbDataAttribute='lfn_db', 
                                              splitHiAndLow=False,
                                              excludeBadChannels=args.excludeBadChannels,
                                              plotBadChannels=args.plotBadChannels,
                                              plotIOVs=args.showIOVStart,
                                              saveADCDetails=args.saveADCDetails)])

g = Go(processList, withMBTS=args.withMBTS, withSpecialMods=args.withSpecialMods, RUN2=args.RUN2)

output.close()

