#!/usr/bin/env bash
macros/cis/CIS_DB_Update.py --date '28 days' --region 'EBA_m40_c35_highgain' 'LBC_m57_c06_highgain' --ldate 457083 457543 457650 
cd results
ReadCalibFromCool.py --schema="sqlite://;schema=tileSqlite.db;dbname=CONDBR2" --folder=/TILE/OFL02/CALIB/CIS/LIN --tag=UPD1 | grep -v miss > Recal.txt
grep 'EBA40 35 1' Recal.txt >> toRecalibrate.txt
grep 'LBC57  6 1' Recal.txt >> toRecalibrate.txt
rm tileSqlite.db CIS_DB_update.txt Recal.txt
cd ..
macros/cis/CIS_DB_Update.py --date '28 days' --region 'LBA_m38_c05_highgain' --ldate 457543 457650 
cd results
ReadCalibFromCool.py --schema="sqlite://;schema=tileSqlite.db;dbname=CONDBR2" --folder=/TILE/OFL02/CALIB/CIS/LIN --tag=UPD1 | grep -v miss > Recal.txt
grep 'LBA38  5 1' Recal.txt >> toRecalibrate.txt
rm tileSqlite.db CIS_DB_update.txt Recal.txt
cd ..
