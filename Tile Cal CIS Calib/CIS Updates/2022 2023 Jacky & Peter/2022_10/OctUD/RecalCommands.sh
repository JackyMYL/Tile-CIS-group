#!/usr/bin/env bash
macros/cis/CIS_DB_Update.py --date '28 days' --region 'LBC_m52_c34_highgain' 'LBC_m52_c34_lowgain' --ldate 435269 435290 435722 
cd results
ReadCalibFromCool.py --schema="sqlite://;schema=tileSqlite.db;dbname=CONDBR2" --folder=/TILE/OFL02/CALIB/CIS/LIN --tag=UPD1 | grep -v miss > Recal.txt
grep 'LBC52 34 1' Recal.txt >> toRecalibrate.txt
grep 'LBC52 34 0' Recal.txt >> toRecalibrate.txt
rm tileSqlite.db CIS_DB_update.txt Recal.txt
cd ..
macros/cis/CIS_DB_Update.py --date '28 days' --region 'LBA_m03_c17_lowgain' 'LBA_m51_c12_highgain' --ldate 435722 
cd results
ReadCalibFromCool.py --schema="sqlite://;schema=tileSqlite.db;dbname=CONDBR2" --folder=/TILE/OFL02/CALIB/CIS/LIN --tag=UPD1 | grep -v miss > Recal.txt
grep 'LBA03 17 0' Recal.txt >> toRecalibrate.txt
grep 'LBA51 12 1' Recal.txt >> toRecalibrate.txt
rm tileSqlite.db CIS_DB_update.txt Recal.txt
cd ..
macros/cis/CIS_DB_Update.py --date '28 days' --region 'EBA_m61_c15_highgain' --ldate 433937 434229 434572 434584 435091 435269 435290 435722 
cd results
ReadCalibFromCool.py --schema="sqlite://;schema=tileSqlite.db;dbname=CONDBR2" --folder=/TILE/OFL02/CALIB/CIS/LIN --tag=UPD1 | grep -v miss > Recal.txt
grep 'EBA61 15 1' Recal.txt >> toRecalibrate.txt
rm tileSqlite.db CIS_DB_update.txt Recal.txt
cd ..
