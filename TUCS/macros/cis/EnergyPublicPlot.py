#!/usr/bin/env python
# Author: Grey Wilburn <gwwilburn@gmail.com>
#
# A simple macro used for the tile cell energy deposition
# public plots
#


import argparse
import os

parser = argparse.ArgumentParser(description=
'makes the Tile Cell Energy Deposition 1D public plot. \n \
Has two modes: Default mode extracts cell energy from EOS root files w/ \n \
D3PD ntuples and saves a histogram in a local root file. "Combination" \n \
mode reads multiple such local root files and makes the public plot \n \
with distributions from multuple sources (e.g., data, mc, random trigger). \n \
Idea is to only read the D3PD\'s once, save the info to a small local root file, \n \
and then read these small local root files when formatting the final plot.',
formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('--combination', action='store_true', default=False,
                    help=
'Use this option to run the CellEnergyFinal.py worker, which reads local \n \
root files with premade cell energy deposition histograms. This is the \n \
worker that makes the public plots. Otherwise, the CellEnergy.py worker \n \
will be used, which reads from individual D3PD\'s and creats said local \n \
root files')

os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

args=parser.parse_args()
if args.combination:
    cellenergy = CellEnergyFinal()
else:
    cellenergy = CellEnergy()

runs = 263977
selected_region = ""

Go([ 
    Use(run=runs, region=selected_region, runType = "CIS"),
    ReadCIS(),
    CleanCIS(),
    cellenergy
    ])



