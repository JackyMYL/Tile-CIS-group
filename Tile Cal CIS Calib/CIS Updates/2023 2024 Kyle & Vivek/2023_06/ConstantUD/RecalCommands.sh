#!/usr/bin/env bash
macros/cis/CIS_DB_Update.py --date '28 days' --region 'EBA_m19_c41_highgain' 'EBA_m40_c35_highgain' 'LBA_m54_c06_highgain' 'LBC_m28_c04_lowgain' 'LBC_m48_c00_lowgain' --ldate 455563 455913 
cd results
ReadCalibFromCool.py --schema="sqlite://;schema=tileSqlite.db;dbname=CONDBR2" --folder=/TILE/OFL02/CALIB/CIS/LIN --tag=UPD1 | grep -v miss > Recal.txt
grep 'EBA19 41 1' Recal.txt >> toRecalibrate.txt
grep 'EBA40 35 1' Recal.txt >> toRecalibrate.txt
grep 'LBA54  6 1' Recal.txt >> toRecalibrate.txt
grep 'LBC28  4 0' Recal.txt >> toRecalibrate.txt
grep 'LBC48  0 0' Recal.txt >> toRecalibrate.txt
rm tileSqlite.db CIS_DB_update.txt Recal.txt
cd ..
macros/cis/CIS_DB_Update.py --date '28 days' --region 'EBC_m56_c41_lowgain' 'LBC_m20_c37_highgain' 'LBC_m20_c37_lowgain' --ldate 455913 
cd results
ReadCalibFromCool.py --schema="sqlite://;schema=tileSqlite.db;dbname=CONDBR2" --folder=/TILE/OFL02/CALIB/CIS/LIN --tag=UPD1 | grep -v miss > Recal.txt
grep 'EBC56 41 0' Recal.txt >> toRecalibrate.txt
grep 'LBC20 37 1' Recal.txt >> toRecalibrate.txt
grep 'LBC20 37 0' Recal.txt >> toRecalibrate.txt
rm tileSqlite.db CIS_DB_update.txt Recal.txt
cd ..
