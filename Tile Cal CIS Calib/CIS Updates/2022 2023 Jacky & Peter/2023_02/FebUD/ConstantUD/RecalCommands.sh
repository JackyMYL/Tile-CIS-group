#!/usr/bin/env bash
macros/cis/CIS_DB_Update.py --date '28 days' --region 'EBA_m40_c30_highgain' 'EBA_m40_c31_highgain' 'EBA_m40_c32_highgain' 'EBA_m40_c37_highgain' 'EBA_m40_c38_highgain' 'EBA_m40_c39_highgain' 'EBA_m40_c40_highgain' 'EBA_m40_c30_lowgain' 'EBA_m40_c31_lowgain' 'EBA_m40_c32_lowgain' 'EBA_m40_c37_lowgain' 'EBA_m40_c38_lowgain' 'EBA_m40_c39_lowgain' 'EBA_m40_c40_lowgain' 'EBA_m40_c35_lowgain' 'EBA_m40_c36_highgain' 'EBA_m40_c41_highgain' 'EBA_m61_c15_highgain' 'EBA_m61_c15_lowgain' 'LBC_m49_c24_highgain' 'LBC_m49_c25_highgain' 'LBC_m49_c26_highgain' 'LBC_m49_c27_highgain' 'LBC_m49_c28_highgain' 'LBC_m49_c29_highgain' 'LBC_m49_c33_highgain' 'LBC_m49_c34_highgain' 'LBC_m49_c35_highgain' 'LBC_m49_c24_lowgain' 'LBC_m49_c25_lowgain' 'LBC_m49_c26_lowgain' 'LBC_m49_c27_lowgain' 'LBC_m49_c28_lowgain' 'LBC_m49_c29_lowgain' 'LBC_m49_c33_lowgain' 'LBC_m49_c34_lowgain' 'LBC_m49_c35_lowgain' 'LBC_m52_c34_highgain' 'LBC_m52_c34_lowgain' --ldate 443831 443835 444001 444007 444633 
cd results
ReadCalibFromCool.py --schema="sqlite://;schema=tileSqlite.db;dbname=CONDBR2" --folder=/TILE/OFL02/CALIB/CIS/LIN --tag=UPD1 | grep -v miss > Recal.txt
grep 'EBA40 30 1' Recal.txt >> toRecalibrate.txt
grep 'EBA40 31 1' Recal.txt >> toRecalibrate.txt
grep 'EBA40 32 1' Recal.txt >> toRecalibrate.txt
grep 'EBA40 37 1' Recal.txt >> toRecalibrate.txt
grep 'EBA40 38 1' Recal.txt >> toRecalibrate.txt
grep 'EBA40 39 1' Recal.txt >> toRecalibrate.txt
grep 'EBA40 40 1' Recal.txt >> toRecalibrate.txt
grep 'EBA40 30 0' Recal.txt >> toRecalibrate.txt
grep 'EBA40 31 0' Recal.txt >> toRecalibrate.txt
grep 'EBA40 32 0' Recal.txt >> toRecalibrate.txt
grep 'EBA40 37 0' Recal.txt >> toRecalibrate.txt
grep 'EBA40 38 0' Recal.txt >> toRecalibrate.txt
grep 'EBA40 39 0' Recal.txt >> toRecalibrate.txt
grep 'EBA40 40 0' Recal.txt >> toRecalibrate.txt
grep 'EBA40 35 0' Recal.txt >> toRecalibrate.txt
grep 'EBA40 36 1' Recal.txt >> toRecalibrate.txt
grep 'EBA40 41 1' Recal.txt >> toRecalibrate.txt
grep 'EBA61 15 1' Recal.txt >> toRecalibrate.txt
grep 'EBA61 15 0' Recal.txt >> toRecalibrate.txt
grep 'LBC49 24 1' Recal.txt >> toRecalibrate.txt
grep 'LBC49 25 1' Recal.txt >> toRecalibrate.txt
grep 'LBC49 26 1' Recal.txt >> toRecalibrate.txt
grep 'LBC49 27 1' Recal.txt >> toRecalibrate.txt
grep 'LBC49 28 1' Recal.txt >> toRecalibrate.txt
grep 'LBC49 29 1' Recal.txt >> toRecalibrate.txt
grep 'LBC49 33 1' Recal.txt >> toRecalibrate.txt
grep 'LBC49 34 1' Recal.txt >> toRecalibrate.txt
grep 'LBC49 35 1' Recal.txt >> toRecalibrate.txt
grep 'LBC49 24 0' Recal.txt >> toRecalibrate.txt
grep 'LBC49 25 0' Recal.txt >> toRecalibrate.txt
grep 'LBC49 26 0' Recal.txt >> toRecalibrate.txt
grep 'LBC49 27 0' Recal.txt >> toRecalibrate.txt
grep 'LBC49 28 0' Recal.txt >> toRecalibrate.txt
grep 'LBC49 29 0' Recal.txt >> toRecalibrate.txt
grep 'LBC49 33 0' Recal.txt >> toRecalibrate.txt
grep 'LBC49 34 0' Recal.txt >> toRecalibrate.txt
grep 'LBC49 35 0' Recal.txt >> toRecalibrate.txt
grep 'LBC52 34 1' Recal.txt >> toRecalibrate.txt
grep 'LBC52 34 0' Recal.txt >> toRecalibrate.txt
rm tileSqlite.db CIS_DB_update.txt Recal.txt
cd ..
macros/cis/CIS_DB_Update.py --date '28 days' --region 'EBC_m34_c30_highgain' 'EBC_m34_c31_highgain' 'EBC_m34_c32_highgain' 'EBC_m34_c35_highgain' 'EBC_m34_c36_highgain' 'EBC_m34_c37_highgain' 'EBC_m34_c30_lowgain' 'EBC_m34_c31_lowgain' 'EBC_m34_c32_lowgain' 'EBC_m34_c35_lowgain' 'EBC_m34_c36_lowgain' 'EBC_m34_c37_lowgain' 'LBC_m17_c06_highgain' 'LBC_m17_c07_highgain' 'LBC_m17_c08_highgain' 'LBC_m17_c06_lowgain' 'LBC_m17_c07_lowgain' 'LBC_m17_c08_lowgain' --ldate 443414 443831 443835 444001 444007 444633 
cd results
ReadCalibFromCool.py --schema="sqlite://;schema=tileSqlite.db;dbname=CONDBR2" --folder=/TILE/OFL02/CALIB/CIS/LIN --tag=UPD1 | grep -v miss > Recal.txt
grep 'EBC34 30 1' Recal.txt >> toRecalibrate.txt
grep 'EBC34 31 1' Recal.txt >> toRecalibrate.txt
grep 'EBC34 32 1' Recal.txt >> toRecalibrate.txt
grep 'EBC34 35 1' Recal.txt >> toRecalibrate.txt
grep 'EBC34 36 1' Recal.txt >> toRecalibrate.txt
grep 'EBC34 37 1' Recal.txt >> toRecalibrate.txt
grep 'EBC34 30 0' Recal.txt >> toRecalibrate.txt
grep 'EBC34 31 0' Recal.txt >> toRecalibrate.txt
grep 'EBC34 32 0' Recal.txt >> toRecalibrate.txt
grep 'EBC34 35 0' Recal.txt >> toRecalibrate.txt
grep 'EBC34 36 0' Recal.txt >> toRecalibrate.txt
grep 'EBC34 37 0' Recal.txt >> toRecalibrate.txt
grep 'LBC17  6 1' Recal.txt >> toRecalibrate.txt
grep 'LBC17  7 1' Recal.txt >> toRecalibrate.txt
grep 'LBC17  8 1' Recal.txt >> toRecalibrate.txt
grep 'LBC17  6 0' Recal.txt >> toRecalibrate.txt
grep 'LBC17  7 0' Recal.txt >> toRecalibrate.txt
grep 'LBC17  8 0' Recal.txt >> toRecalibrate.txt
rm tileSqlite.db CIS_DB_update.txt Recal.txt
cd ..
