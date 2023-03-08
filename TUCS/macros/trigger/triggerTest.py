#!/usr/bin/env python
# author: Bernardo Sotto-Maior Peralva <bernardo@cern.ch>
# date: July 30, 2010
# Macro to run trigger channel analysis and update the trigger bits in TileCal database.

"Trigger macro for single run"

import os
import argparse
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

parser = argparse.ArgumentParser(description=
'Run trigger PMT scan analysis for one single run',
formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('--runNumber', action='store',nargs='+', type=int, default=0,
                    help=
'Select run to use specifying the run number \n\
EX: --runNumber 228863 ')

parser.add_argument('--gainCuts', action='store', nargs='+', type=float, 
                    help=
'Allows you to select the cut value for defining zero-gain and low-gain channels  \n\
The two values should be separated by white space \n\
Note: the order is not important (the lowest value is always used to define the zero-gain cut \n\
EX: --gainCuts 0.1 0.5 ')

parser.add_argument('--inputDir', action='store', type=str, 
                    help=
'Allows you to specify the input directory for the L1Calo PMT scan ntuples  \n\
If not specified the default directory /afs/cern.ch/user/t/tilecali/w0/ntuples/l1calo will be used \n\
EX: --inputDirectory \'./\' ')

args=parser.parse_args()

if args.runNumber:
    if len(args.runNumber) == 1:
        runList = args.runNumber[0]
    else:
        print('\
        --RUNNUMBER HAS TOO MANY ARGUMENTS \n\
USING ONLY THE FIRST')
        runList = args.runNumber[0]
else:
    runList = args.runNumber

if args.gainCuts:
    if len(args.gainCuts) == 2:
        gainCuts = args.gainCuts
    else:
        print('\ --gainCuts should have two arguments, using the default values')
        gainCuts = [0.1, 0.5]
else:
    gainCuts = [0.1, 0.5]

if args.inputDir:
    inputDir = args.inputDir
else:
    inputDir = '/afs/cern.ch/user/t/tilecali/w0/ntuples/l1calo'

zeroGain = min(gainCuts[0], gainCuts[1])
lowGain = max(gainCuts[0], gainCuts[1])
print("Running over run# ", runList ," with zeroGain cut ", zeroGain, " and lowGain cut ", lowGain, ", inputDir: ", inputDir)

#********************* Single Run Setup - If you want to look at a particular run ******************
## This is for only one run in case you want to check the plots for mapping, PMT mean and RMS distributions and etc... 
## All plots are in plots/latest/print/ and you will see the date you ran TUCS for this particular run
u=Use(run=runList,runType='L1Calo')
processList = [u, ReadTriggerChannelFile(processingDir=inputDir),
                 DefineTriggerCuts(zeroGainCutValue = zeroGain, lowGainCutValue = lowGain),
                 PrintTriggerBadChannels(zeroGainCutValue = zeroGain, lowGainCutValue = lowGain)]
#***************************************************************************************************

g = Go(processList)
