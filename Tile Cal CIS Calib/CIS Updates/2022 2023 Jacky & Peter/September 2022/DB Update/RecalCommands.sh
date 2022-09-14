#!/usr/bin/env bash
macros/cis/CIS_DB_Update.py --date '28 days' --region 'LBC_m24_c00_lowgain' 'LBC_m24_c01_lowgain' 'LBC_m24_c02_lowgain' 'LBC_m24_c03_lowgain' 'LBC_m24_c04_lowgain' 'LBC_m24_c05_lowgain' 'LBC_m24_c06_lowgain' 'LBC_m24_c07_lowgain' 'LBC_m24_c08_lowgain' 'LBC_m24_c09_lowgain' 'LBC_m24_c10_lowgain' 'LBC_m24_c11_lowgain' 'LBC_m24_c12_lowgain' 'LBC_m24_c13_lowgain' 'LBC_m24_c14_lowgain' 'LBC_m24_c15_lowgain' 'LBC_m24_c16_lowgain' 'LBC_m24_c17_lowgain' 'LBC_m24_c18_lowgain' 'LBC_m24_c19_lowgain' 'LBC_m24_c20_lowgain' 'LBC_m24_c21_lowgain' 'LBC_m24_c22_lowgain' 'LBC_m24_c23_lowgain' 'LBC_m24_c24_lowgain' 'LBC_m24_c25_lowgain' 'LBC_m24_c26_lowgain' 'LBC_m24_c27_lowgain' 'LBC_m24_c28_lowgain' 'LBC_m24_c29_lowgain' 'LBC_m24_c30_lowgain' 'LBC_m24_c31_lowgain' 'LBC_m24_c32_lowgain' 'LBC_m24_c33_lowgain' 'LBC_m24_c34_lowgain' 'LBC_m24_c35_lowgain' 'LBC_m24_c36_lowgain' 'LBC_m24_c37_lowgain' 'LBC_m24_c38_lowgain' 'LBC_m24_c39_lowgain' 'LBC_m24_c40_lowgain' 'LBC_m24_c41_lowgain' 'LBC_m24_c42_lowgain' 'LBC_m24_c43_lowgain' 'LBC_m24_c44_lowgain' 'LBC_m24_c45_lowgain' 'LBC_m24_c46_lowgain' 'LBC_m24_c47_lowgain' --ldate 432218 432548 432824 
cd ~/private/Tucs/results
ReadCalibFromCool.py --schema="sqlite://;schema=tileSqlite.db;dbname=CONDBR2" --folder=/TILE/OFL02/CALIB/CIS/LIN --tag=UPD1 | grep -v miss > Recal.txt
grep 'LBC24  0 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24  1 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24  2 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24  3 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24  4 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24  5 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24  6 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24  7 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24  8 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24  9 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 10 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 11 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 12 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 13 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 14 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 15 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 16 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 17 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 18 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 19 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 20 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 21 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 22 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 23 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 24 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 25 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 26 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 27 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 28 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 29 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 30 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 31 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 32 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 33 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 34 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 35 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 36 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 37 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 38 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 39 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 40 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 41 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 42 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 43 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 44 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 45 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 46 0' Recal.txt >> toRecalibrate.txt
grep 'LBC24 47 0' Recal.txt >> toRecalibrate.txt
rm tileSqlite.db CIS_DB_update.txt Recal.txt
cd ~/private/Tucs
macros/cis/CIS_DB_Update.py --date '28 days' --region 'EBC_m46_c07_lowgain' --ldate 432548 432824 
cd ~/private/Tucs/results
ReadCalibFromCool.py --schema="sqlite://;schema=tileSqlite.db;dbname=CONDBR2" --folder=/TILE/OFL02/CALIB/CIS/LIN --tag=UPD1 | grep -v miss > Recal.txt
grep 'EBC46  7 0' Recal.txt >> toRecalibrate.txt
rm tileSqlite.db CIS_DB_update.txt Recal.txt
cd ~/private/Tucs
macros/cis/CIS_DB_Update.py --date '28 days' --region 'LBC_m52_c00_lowgain' 'LBC_m52_c01_lowgain' 'LBC_m52_c02_lowgain' 'LBC_m52_c03_lowgain' 'LBC_m52_c04_lowgain' 'LBC_m52_c05_lowgain' 'LBC_m52_c06_lowgain' 'LBC_m52_c07_lowgain' 'LBC_m52_c08_lowgain' 'LBC_m52_c09_lowgain' 'LBC_m52_c10_lowgain' 'LBC_m52_c11_lowgain' 'LBC_m52_c12_lowgain' 'LBC_m52_c13_lowgain' 'LBC_m52_c14_lowgain' 'LBC_m52_c15_lowgain' 'LBC_m52_c16_lowgain' 'LBC_m52_c17_lowgain' 'LBC_m52_c19_lowgain' 'LBC_m52_c20_lowgain' 'LBC_m52_c21_lowgain' 'LBC_m52_c22_lowgain' 'LBC_m52_c23_lowgain' 'LBC_m52_c24_lowgain' 'LBC_m52_c25_lowgain' 'LBC_m52_c26_lowgain' 'LBC_m52_c27_lowgain' 'LBC_m52_c28_lowgain' 'LBC_m52_c29_lowgain' 'LBC_m52_c30_lowgain' 'LBC_m52_c31_lowgain' 'LBC_m52_c32_lowgain' 'LBC_m52_c33_lowgain' 'LBC_m52_c34_lowgain' 'LBC_m52_c35_lowgain' 'LBC_m52_c36_lowgain' 'LBC_m52_c37_lowgain' 'LBC_m52_c38_lowgain' 'LBC_m52_c39_lowgain' 'LBC_m52_c40_lowgain' 'LBC_m52_c41_lowgain' 'LBC_m52_c42_lowgain' 'LBC_m52_c43_lowgain' 'LBC_m52_c44_lowgain' 'LBC_m52_c45_lowgain' 'LBC_m52_c46_lowgain' 'LBC_m52_c47_lowgain' --ldate 432548 432824 
cd ~/private/Tucs/results
ReadCalibFromCool.py --schema="sqlite://;schema=tileSqlite.db;dbname=CONDBR2" --folder=/TILE/OFL02/CALIB/CIS/LIN --tag=UPD1 | grep -v miss > Recal.txt
grep 'LBC52  0 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52  1 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52  2 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52  3 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52  4 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52  5 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52  6 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52  7 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52  8 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52  9 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 10 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 11 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 12 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 13 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 14 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 15 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 16 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 17 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 19 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 20 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 21 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 22 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 23 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 24 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 25 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 26 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 27 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 28 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 29 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 30 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 31 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 32 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 33 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 34 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 35 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 36 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 37 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 38 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 39 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 40 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 41 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 42 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 43 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 44 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 45 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 46 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 47 0' Recal.txt >> toRecalibrate.txt
rm tileSqlite.db CIS_DB_update.txt Recal.txt
cd ~/private/Tucs
