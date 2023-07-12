#!/bin/bash
#simple script for reprocessing. written in bash to avoid problems in python
#Run from Tucs directory!
echo "starting reprocessing"
#4 arguments: run number associated to pedestal, ped number, start of IOV, end of IOV
python macros/noise/MakeReprocessedCellNoise.py 199825 31 199600 -1
python macros/noise/MakeReprocessedCellNoise.py 200561 31 201147 -1
