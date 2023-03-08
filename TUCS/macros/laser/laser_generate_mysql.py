#!/usr/bin/env python

import os, sys, _mysql
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!
exec(open('src/laser/laserGetOpt.py').read(), globals()) 

# Laser Argument class
localArgParser=laserArgs(verbose=True)
# Add local arguments that are specific to this macro
localArgParser.add_local_arg('--newArg', action='store_true',  default=False, arghelp='New argument \n')
# Get arguments from parser 
localArgs=localArgParser.args_from_parser()
newArg=localArgs.newArg

exit()

mysqldb = _mysql.connect(host='pcata007.cern.ch',user='reader')

#mysqldb.query("select run from tile.comminfo where date>='2015-05-01' and ((lasfilter='6' and events>10000) or (lasfilter='8' and events>10000))  and lasreqamp='15000' and type ='Las' and not (recofrags like '%%005%%' or recofrags like '%%50%%' ) and beamfrags like '%%200017%%' and not setup='ATLAS' and comments is NULL ")

mysqldb.query("select run from tile.comminfo where date>='2016-05-25' and (lasfilter='8' and events>10000)  and lasreqamp='15000' and type ='Las' and not (recofrags like '%%005%%' or recofrags like '%%50%%' ) and beamfrags like '%%200017%%' and not setup='ATLAS' and comments is NULL ")



results = mysqldb.store_result()

run = results.fetch_row()[0][0]

schema = 'sqlite://;schema=tileSqliteLAS.db;dbname=CONDBR2'
while run!=None:
    print run
    Go( [Use([run]),
         ReadLaser(diode_num_lg=12, diode_num_hg=13),
         ReadBchFromCool( schema='COOLOFL_TILE/CONDBR2',
                          folder='/TILE/OFL02/STATUS/ADC',
                          tag='UPD4',
                          Fast=True,
                          storeADCinfo=True ),
         ReadCalFromCool( schema='sqlite://;schema=tileSqlite.db;dbname=CONDBR2',
                          folder='/TILE/OFL02/CALIB/CES',
                          runType = 'Las_REF',
                          tag = 'RUN2-HLT-UPD1-01',
                          verbose=True), 
         getGlobalShiftsDirect(siglim=2.0, n_iter=3, verbose=True),
         getFiberShiftsDirect(siglim=2.0, n_iter=3, verbose=True),
         getPMTShiftsDirect(usePisa=True),
         WriteDBNew(input_schema=schema, output_schema=schema, tag='TileOfl02CalibLasLin-RUN2-HLT-UPD1-00',
                    folder='/TILE/OFL02/CALIB/LAS/LIN',iov=(int(run),0), useHighGain=True) ])
    run = results.fetch_row()[0][0]

