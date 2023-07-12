#!/usr/bin/env python

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!
#===========================================================
# This macro allows masking individual components of the TileCalorimeter in the DB
# by replacing their real values by some chosen default
#===========================================================

import optparse
parser = optparse.OptionParser()
parser.add_option('--IOVbeg',       dest="IOVbeg")
parser.add_option('--IOVend',       dest="IOVend",  default=-1)
parser.add_option('--IOVbegLB',       dest="IOVbegLB",  default=0)
parser.add_option('--IOVendLB',       dest="IOVendLB",  default=MAXLBK)
parser.add_option('-T','--dbTag',   dest="dbTag",   default="RUN2-UPD1-00")
parser.add_option('--regionList',   dest="regionList", help="comma-separated list, precede cell hashes with H")

(options, args) = parser.parse_args()

#IOVbeg   = int(options.IOVbeg)
#IOVbegLB = int(options.IOVbegLB)
#IOVend   = int(options.IOVend)
#IOVendLB = int(options.IOVendLB)

dbTag    = options.dbTag

maskList = [ r for r in options.regionList.split(',')]

processList = []
u=Use(run=IOVbeg,region='',type='physical',verbose=True,keepOnlyActive=False)
processList += [u,ReadCellNoiseDB(folderTag=dbTag),MaskComponent(parameter='cell',components=maskList),WriteCellNoiseDB(offline_iov_beg=(options.IOVbeg,options.IOVbegLB),offline_iov_end=(options.IOVend,options.IOVendLB),folderTag=dbTag)]

g = Go(processList)
