#!/usr/bin/env bash
macros/cis/CIS_DB_Update.py --date '28 days' --region 'LBA_m51_c12_highgain' 'LBC_m62_c08_highgain' --ldate 437309 437563 437792 438209 438370 
cd results
ReadCalibFromCool.py --schema="sqlite://;schema=tileSqlite.db;dbname=CONDBR2" --folder=/TILE/OFL02/CALIB/CIS/LIN --tag=UPD1 | grep -v miss > Recal.txt
grep 'LBA51 12 1' Recal.txt >> toRecalibrate.txt
grep 'LBC62  8 1' Recal.txt >> toRecalibrate.txt
rm tileSqlite.db CIS_DB_update.txt Recal.txt
cd ..
