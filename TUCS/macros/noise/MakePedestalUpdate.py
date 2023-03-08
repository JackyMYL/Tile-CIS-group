#!/usr/bin/env python

# TUCS common
import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

import _NoiseCommon

# handle arguments
argparser = _NoiseCommon.common_noise_arguments('Produce new pedestal calibration constants')

# Input arguments
argparser.add_argument('--run', required=True,
                       type=int, help='Specify the run to compare to DB', dest='run')

argparser.add_argument('--db_compare_run', required=False, default=None,
                       type=str, help='Specify the DB comparison run, also the start of the IoV', dest='dbCompareRun')

#argparser.add_argument('--db_IoV_start', required=False, default=None,
#                       type=str, help='Specify the first run of the IoV', dest='dbLowerIoV')

source_grp = argparser.add_mutually_exclusive_group(required=False)
source_grp.add_argument('--source_file', action='store_const', const='File', help='Input from calibration file', dest='inputSource')
source_grp.add_argument('--source_dqmf', action='store_const', const='DQMF', help='Input from DQMF', dest='inputSource')
argparser.set_defaults(inputSource='File')

argparser.add_argument('--dqmf_user_name', required=False,
                       type=str, help='User name for DQMF', dest='dqmf_user_name')

argparser.add_argument('--dqmf_stream', required=False, default='physics_CosmicCalo',
                       type=str, help='Stream for DQMF', dest='dqmf_stream')

argparser.add_argument('--dqmf_source', required=False, default='tier0',
                       type=str, help='Source for DQMF', dest='dqmf_source')

argparser.add_argument('--dqmf_server', required=False, default='atlasdqm.cern.ch',
                       type=str, help='Server for DQMF', dest='dqmf_server')

# Mics. arguments
write_updated_grp = argparser.add_mutually_exclusive_group(required=False)
write_updated_grp.add_argument('--only_write_updated_drawers', action='store_true',
                       help='Only write drawers with updated values', dest='onlyWriteUpdatedDrawers')
write_updated_grp.add_argument('--write_all_drawers', action='store_false',
                       help='Only write drawers with updated values', dest='onlyWriteUpdatedDrawers')
argparser.set_defaults(onlyWriteUpdatedDrawers=True)

# Processing arguments
argparser.add_argument('--lg_ped_threshold', required=False, default=0.5,
                       type=float, help='Pedestal Low gain difference threshold', dest='lgPedThreshold')

argparser.add_argument('--hg_ped_threshold', required=False, default=0.5,
                       type=float, help='Pedestal High gain difference threshold', dest='hgPedThreshold')

argparser.add_argument('--lg_lfn_threshold', required=False, default=-0.5,
                       type=float, help='LFN Low gain difference threshold', dest='lgLFNThreshold')

argparser.add_argument('--hg_lfn_threshold', required=False, default=-0.5,
                       type=float, help='LFN High gain difference threshold', dest='hgLFNThreshold')

argparser.add_argument('--lg_hfn_threshold', required=False, default=-0.5,
                       type=float, help='HFN Low gain difference threshold', dest='lgHFNThreshold')

argparser.add_argument('--hg_hfn_threshold', required=False, default=-0.5,
                       type=float, help='HFN High gain difference threshold', dest='hgHFNThreshold')

# Bad channel arguments
mask_bad_grp = argparser.add_mutually_exclusive_group(required=False)
mask_bad_grp.add_argument('--mask_bad', action='store_true',
                          help='Ignore channels marked as bad', dest='maskBadADC')
mask_bad_grp.add_argument('--include_bad', action='store_false',
                          help='Include channels marked as bad', dest='maskBadADC')
argparser.set_defaults(maskBadADC=True)

# drawers to include / exclude
incl_excl_grp = argparser.add_mutually_exclusive_group(required=False)
incl_excl_grp.add_argument('--include_drawers', type=str, default=None,
                          help='', dest='include_drawers')
incl_excl_grp.add_argument('--exclude_drawers', type=str, default=None,
                          help='', dest='exclude_drawers')

# Output arguments
argparser.add_argument('--output_iov_run', required=False, default=-1,
                       type=int, help='Start IOV run number for the result, default is input run number', dest='output_iov_run')

argparser.add_argument('--output', required=False, 
                       type=str, help='Output SQLite file', dest='output')

argparser.add_argument('--output_db_conn', required=False, default='CONDBR2',
                       type=str, help='Output SQLite DB', dest='outputDbConn')

argparser.add_argument('--summary_output', required=False, default='',
                       type=str, help='Summary log file', dest='summaryOutput')

write_summary_grp = argparser.add_mutually_exclusive_group(required=False)
write_summary_grp.add_argument('--write_summary', action='store_true',
                       help='Write summary log', dest='writeSummary')
write_summary_grp.add_argument('--do_not_write_summary', action='store_false',
                       help='Do not write summary log', dest='writeSummary')
argparser.set_defaults(writeSummary=True)

do_plot_grp = argparser.add_mutually_exclusive_group(required=False)
do_plot_grp.add_argument('--plot', action='store_true',
                       help='Plot', dest='doPlot')
do_plot_grp.add_argument('--do_not_plot', action='store_false',
                       help='Do not plot', dest='doPlot')
argparser.set_defaults(doPlot=True)

# If zeros should be replaces by the current DB value
do_plot_grp = argparser.add_mutually_exclusive_group(required=False)
do_plot_grp.add_argument('--keep_db_val_if_zero', action='store_true',
                       help='Keep DB value if zero (checks ped, hfn and lfn)', dest='keepDBValueWhenZero')
do_plot_grp.add_argument('--do_not_keep_db_val_if_zero', action='store_false',
                       help='Ignore zero values', dest='keepDBValueWhenZero')
argparser.set_defaults(keepDBValueWhenZero=False)

args = argparser.parse_args()

if args.output_iov_run < 0:
    args.output_iov_run = args.run

# Determine directories, init summary log and ROOT file output
outputDirectory = _NoiseCommon.determine_output_directory(args)

summary_log_file_name = None
if args.writeSummary:
    if not args.summaryOutput:
        summary_log_file_name = os.path.join(outputDirectory, "tile_pedestal_update_summary_%d.txt" % args.run)
    else:
        summary_log_file_name = os.path.join(outputDirectory, args.summaryOutput)

do_plot = args.doPlot
plot_directory = _NoiseCommon.determine_plot_directory(args) if do_plot else None

root_file_name = None
if not args.outputRoot:
    root_file_name = os.path.join(outputDirectory, 'Pedestal_%d.root' % args.run)
else:
    root_file_name = os.path.join(outputDirectory, args.outputRoot)

output = _NoiseCommon.NoiseOutput(summary_log_file_name, root_file_name, plot_directory)
_NoiseCommon.check_common_arguments(args, output)
output.print_log("Using output directory: %s" %(outputDirectory))

# always print argument values
arg_dict = vars(args)
for k in arg_dict:
    output.print_log("%s : %s" % (str(k), arg_dict[k]))

# Determine parameters
if args.inputSource == 'DQMF':
    if not args.dqmf_user_name or args.dqmf_user_name=='':
        output.print_log("Error: --dqmf_user_name required")
        exit(1)
    if not os.getenv('DQMPWD'):
        output.print_log("Error: --source_dqmf requires a DQMF password set in the environment variable DQMPWD. Note: A DQMF specific password is needed.")
        exit(1)

do_mask_bad = args.maskBadADC
do_patch_bad_values = args.patchBadValues
do_output = args.output and (args.output != '')
if do_output and not args.output_iov_run:
    output.print_log("Error: --output_iov_run required together with --output")
    exit(1)

runNumber = args.run
selected_region = ''

noise_comparison_mode = 'relative' if args.noiseComparisonModeRelative else 'absolute'
output.print_log("Using comparison mode '%s' for noise" % noise_comparison_mode)

# Setup workers
processList = []

if args.inputSource == 'File':
    filename = '/afs/cern.ch/user/t/tilecali/w0/ntuples/ped/Digi_NoiseCalib_1_%s_Ped.root' % (runNumber)
    output.print_log("Reading file: %s" % filename)
    processList.extend([Use(run=runNumber, runType='Ped', type='physical', region=selected_region, verbose=args.verbose, keepOnlyActive=True),
                        ReadDigiNoiseDB(runType = 'Ped', useSqlite=args.dbUseSqlite, dbConn=args.dbConn, dbFile=args.dbSqliteFile,
                                        load_autocr = False, folderTag=args.dbFolderTag,
                                        IOVRun=args.dbCompareRun),
                        ReadDigiNoiseFile(processingDir = filename, load_autocr = False, pedNr = 0)])
elif args.inputSource == 'DQMF':
    output.print_log("Reading from DQMF")
    processList.extend([Use(run=runNumber, runType='Ped', type='physical', region=selected_region, verbose=args.verbose, keepOnlyActive=True),
                        UseDQMF(output, run_number=runNumber, run_type='Ped', user_name=args.dqmf_user_name, verbose=args.verbose, stream=args.dqmf_stream, server=args.dqmf_server, source=args.dqmf_source),
                        ReadDigiNoiseDB(runType = 'Ped', useSqlite=args.dbUseSqlite, dbConn=args.dbConn, dbFile=args.dbSqliteFile,
                                        load_autocr = False, folderTag=args.dbFolderTag,
                                        IOVRun=args.dbCompareRun),
                        ReadDigiNoiseDQMF(output, user_name=args.dqmf_user_name, run_type='Ped', stream=args.dqmf_stream, server=args.dqmf_server, source=args.dqmf_source)])
else:
    output.print_log("Error: Invalid source %s" % args.inputSource)
    exit(1)

if do_mask_bad:
    output.print_log("Do not trigger write of masked channels. Use bad channel schema %s with tag %s." % (args.badChannelSchema, args.badChannelTag))
    processList.append(ReadBadChFromCool(schema=args.badChannelSchema, tag=args.badChannelTag, Fast=True, storeADCinfo=True))

if do_patch_bad_values:
    output.print_log("Patch bad values by checking noise attribute '%s'" % args.badChannelAttribute) 
    processList.append(PatchBadValues(runType = 'Ped', type = 'readout', standard_p=args.badChannelAttribute))

processList.append(CheckSpecialChannels())
processList.append(NoiseVsDB(parameter='digi', savePlot=True, load_autocr = False))

if do_plot:
    output.print_log("Making plots in directory: %s" % plot_directory)
    processList.extend([PedestalComparison2D(referenceRun=runNumber, comparisonRun=runNumber, 
                                             output=output,
                                             maxDiff = 2, minDiff = 0, mode='absolute',
                                             useSimpleColors=False, markBadChannels=False,
                                             referenceRunAttribute='ped_db', comparisonRunAttribute='ped',
                                             plotTitle='Pedestal', referenceRunType='Ped', comparisonRunType='Ped'),
                        PedestalComparison2D(referenceRun=runNumber, comparisonRun=runNumber, 
                                             output=output,
                                             maxDiff = 1, minDiff = 0, mode=noise_comparison_mode,
                                             useSimpleColors=False, markBadChannels=False,
                                             referenceRunAttribute='hfn_db', comparisonRunAttribute='hfn',
                                             plotTitle='HFNoise', referenceRunType='Ped', comparisonRunType='Ped', diffDistMax=1),
                        PedestalComparison2D(referenceRun=runNumber, comparisonRun=runNumber, 
                                             output=output,
                                             maxDiff = 1, minDiff = 0, mode=noise_comparison_mode,
                                             useSimpleColors=False, markBadChannels=False,
                                             referenceRunAttribute='lfn_db', comparisonRunAttribute='lfn',
                                             plotTitle='LFNoise', referenceRunType='Ped', comparisonRunType='Ped', diffDistMax=1)
                        ])

processList.append(PedestalCompare2DB(hgThresholds=[args.hgPedThreshold, args.hgLFNThreshold, args.hgHFNThreshold],
                                      lgThresholds=[args.lgPedThreshold, args.lgLFNThreshold, args.lgHFNThreshold],
                                      isRelativeThreshold =[False, args.noiseComparisonModeRelative, args.noiseComparisonModeRelative],
                                      verbose=args.verbose, 
                                      attributes=['ped', 'lfn', 'hfn'], 
                                      dbAttributes=['ped_db', 'lfn_db', 'hfn_db'], 
                                      maskBad=do_mask_bad,
                                      output=output,
                                      createUpdateEvent=False, runTypeUpdate='PedUpdate', runTypeDB='Ped',
                                      onlyWriteUpdated=args.onlyWriteUpdatedDrawers,
                                      hgLargeDiffThresholds=[10, -1, -1],
                                      lgLargeDiffThresholds=[10, -1, -1],
                                      includeDrawers=args.include_drawers,
                                      keepDBValueForZero=args.keepDBValueWhenZero))

if do_output:
    output.print_log("Write output to SQLite file %s with db %s and IOV from %d using tag %s." % (args.output, args.outputDbConn, args.output_iov_run, args.dbFolderTag))
    processList.append(WriteDigiNoiseDB(load_autocr=False, offline_iov_beg=(args.output_iov_run, 0), folderTag=args.dbFolderTag, 
                                        folderTagAC='', dbConn=args.outputDbConn, sqlfn=args.output, 
                                        onlyWriteUpdated=args.onlyWriteUpdatedDrawers, verbose=args.verbose, outputDirectory=outputDirectory))


g = Go(processList, withMBTS=args.withMBTS, withSpecialMods=args.withSpecialMods, RUN2=args.RUN2)

output.close()
