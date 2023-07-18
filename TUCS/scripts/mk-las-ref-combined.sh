#/bin/bash -x

NOW=`date "+%Y%m%d-%H%M%S"`

AtlCoolCopy 'COOLOFL_TILE/CONDBR2' "sqlite://;schema=tileSqlite-combined.db;dbname=CONDBR2" -folder /TILE/OFL02/CALIB/CES -r 257369 -t TileOfl02CalibCes-RUN2-HLT-UPD1-01 -nrls 248373  0 -a -create

rm -i tileSqlite.db
ln -sf tileSqlite-combined.db tileSqlite.db



## 2016 reference
#reference runs 2016-05-25 
macros/laser/laser_stab_references.py --low=300124 --high=300125 --iov=248374
#For the gain reference we take mean 2 week before
macros/laser/laser_stab_references_PMTgain.py --date=2016-05-11 --enddate=2016-05-25 --iov=248375

## 2017 reference
# Recent 2017 runs for 2017 reference 2017-05-23
macros/laser/laser_stab_references.py --low=324293 --high=324295 --iov=314246
macros/laser/laser_stab_references_PMTgain.py --date=2017-05-08 --enddate=2017-05-23 --iov=314247
macros/laser/laser_stab_references.py --low=331047 --high=331050 --iov=330785 --E3E4

## 2018 reference (matching Cs scan of 2018-02-17)
macros/laser/laser_stab_references.py --low=344221 --high=344222 --iov=344221
macros/laser/laser_stab_references_PMTgain.py --date=2018-02-05 --enddate=2018-02-25 --iov=344221
