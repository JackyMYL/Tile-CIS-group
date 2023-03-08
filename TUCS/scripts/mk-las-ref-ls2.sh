#/bin/bash 

NOW=`date "+%Y%m%d-%H%M%S"` 


#AtlCoolCopy.exe 'COOLOFL_TILE/CONDBR2' "sqlite://;schema=tileSqlite.db;dbname=CONDBR2" -folder /TILE/OFL02/CALIB/CES -r 257369 -t TileOfl02CalibCes-RUN2-HLT-UPD1-01 -nrls 248373  0 -a -create

# First laser run in 2019: 367998

AtlCoolCopy 'COOLOFL_TILE/CONDBR2' "sqlite://;schema=tileSqlite-${NOW}.db;dbname=CONDBR2" -folder /TILE/OFL02/CALIB/CES -r 367998 -t TileOfl02CalibCes-RUN2-HLT-UPD1-01 -nrls 0  0 -a -create

ln -sf tileSqlite-$NOW.db tileSqlite.db

macros/laser/laser_stab_references_PMTgain.py --date=2020-08-14 --enddate=2020-09-01 --iov=1
macros/laser/laser_stab_references.py --low=381074 --high=381075 --iov=2       # 14th of August 2020 runs
macros/laser/laser_stab_references.py --low=385394 --high=385395 --region=LBA_m18,LBC_m18 --iov=3 #LBC18 Truned on only in Octobre 2020
macros/laser/laser_stab_references.py --low=385563 --high=385565 --region=EBA_m15 --iov=4 # fibre fixed
macros/laser/laser_stab_references.py --low 387197 --high 387198 --iov=5  --MBTS # MBTS HV On in January 2021
macros/laser/laser_stab_references.py --low=392463 --high=392464 --region=EBA_m34,EBA_m44,LBA_m06,LBC_m06,LBA_m58,LBC_m58 --iov=6 # clear fibre fix, HV 
macros/laser/laser_stab_references.py --low=393363 --high=393364 --region=LBA_m14,LBC_m14 --iov=7 # Stable demonstrator
macros/laser/laser_stab_references.py --low=397433 --high=397434 --region=EBA_m54 --iov=8
macros/laser/laser_stab_references.py --low=392381 --high=392381 --region=EBA_m49 --iov=391918 #Clear fibre    
macros/laser/laser_stab_references.py --low=396297 --high=396297 --region=LBA_m14,LBC_m14 --iov=395844 # Demonstrator after intervention 2021-06-24 17:20:58	
macros/laser/laser_stab_references.py --low=398157 --high=398158 --region=LBA_m14,LBC_m14 --iov=398150 # Demonstrator after intervention 2021-07-27 
macros/laser/laser_stab_references.py --low=399293 --high=399294 --region=EBA_m61,EBA_m63 --iov=399000 # Jump clear fibre 
macros/laser/laser_stab_references.py --low=405269 --high=405270 --region=LBA_m14,LBC_m14 --iov=402200 # 2021-09-27, HV change was 26/09 a bit after 4pm
# New optical densities
macros/laser/laser_stab_references.py --low=413589 --high=413590 --iov=413300

# EB HV update 414528 March 21st
macros/laser/laser_stab_references.py --low=415172 --high=415173 --iov=414528	
#LB HV update 415174 March 24th
macros/laser/laser_stab_references.py --low=417172 --high=417173 --iov=415174
macros/laser/laser_stab_references_PMTgain.py --date=2022-04-01 --enddate=2022-04-15 --iov=415175
#macros/laser/laser_stab_references.py --low-417887 --high=417888 --region=EBC_m43 --iov=417797
