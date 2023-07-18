#/bin/bash 

NOW=`date "+%Y%m%d-%H%M%S"`
#AtlCoolCopy.exe 'COOLOFL_TILE/CONDBR2' "sqlite://;schema=tileSqlite.db;dbname=CONDBR2" -folder /TILE/OFL02/CALIB/CES -r 257369 -t TileOfl02CalibCes-RUN2-HLT-UPD1-01 -nrls 248373  0 -a -create

AtlCoolCopy 'COOLOFL_TILE/CONDBR2' "sqlite://;schema=tileSqlite.db;dbname=CONDBR2" -folder /TILE/OFL02/CALIB/CES -r 257369 -t TileOfl02CalibCes-RUN2-HLT-UPD1-01 -nrls 248373  0 -a -create


cp tileSqlite.db tileSqlite.db-$NOW

NOW=`date "+%Y%m%d-%H%M%S"`
macros/laser/laser_stab_references.py --low=$1 --high=$2 --iov=248374
cp tileSqlite.db tileSqlite.db-$NOW



