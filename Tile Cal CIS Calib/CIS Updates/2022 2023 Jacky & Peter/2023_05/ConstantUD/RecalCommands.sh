#!/usr/bin/env bash
macros/cis/CIS_DB_Update.py --date '28 days' --region 'EBA_m49_c00_highgain' --ldate 453591 453841 454106 
cd results
ReadCalibFromCool.py --schema="sqlite://;schema=tileSqlite.db;dbname=CONDBR2" --folder=/TILE/OFL02/CALIB/CIS/LIN --tag=UPD1 | grep -v miss > Recal.txt
grep 'EBA49  0 1' Recal.txt >> toRecalibrate.txt
rm tileSqlite.db CIS_DB_update.txt Recal.txt
cd ..
macros/cis/CIS_DB_Update.py --date '28 days' --region 'LBA_m37_c21_highgain' --ldate 451772 452058 452062 452248 452747 452822 453018 453147 453263 453591 453841 454106 
cd results
ReadCalibFromCool.py --schema="sqlite://;schema=tileSqlite.db;dbname=CONDBR2" --folder=/TILE/OFL02/CALIB/CIS/LIN --tag=UPD1 | grep -v miss > Recal.txt
grep 'LBA37 21 1' Recal.txt >> toRecalibrate.txt
rm tileSqlite.db CIS_DB_update.txt Recal.txt
cd ..
