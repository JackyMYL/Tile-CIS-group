#!/usr/bin/env python

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

#x1 = ReadCsFile(processingDir="/afs/cern.ch/user/t/tilecali/w0/ntuples/cs")

# good runs taken in June 2009, no B field
u1 = Use(run=[1292,1295,1296,1299,1307,1309,1310,1300,1306,1308],runType='cesium',region='EBC_m19',cscomment='',keepOnlyActive=True)
#u1 = Use(run=123000,runType='cesium',region='EBC_m18',cscomment='',keepOnlyActive=False)

# good runs taken in June 2009, B field 'sol+tor'
#u1 = UseCs(run=[1311,1316,1319,1312,1314,1317,1313,1315,1318],runType='cesium',region='LBA',cscomment='sol+tor')

x1 = ReadCsFile(processingDir="/data/cs",normalize=True)

r1 = ReadCalibFromCool(schema = 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2' ,runType='integrator',tag='RUN2-HLT-UPD1-00', folder = '/TILE/OFL02/INTEGRATOR')
r2 = ReadCalibFromCool(schema = 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2',runType='cesium', folder = '/TILE/OFL02/CALIB/CES' , tag='RUN2-HLT-UPD1-01')

qc = CsQC()
#w1 = WriteCsDB(offline_tag='RUN2-HLT-UPD1-01',offline_iov = 'use latest run',register=False,\
#               def_iov=75815,threshold=0.05)

w1 = WriteDB(runType='cesium',offline_tag='RUN2-HLT-UPD1-01',version=2)
p1 = Print()



processors = [ u1, x1, r1, r2, qc]
Go(processors)


