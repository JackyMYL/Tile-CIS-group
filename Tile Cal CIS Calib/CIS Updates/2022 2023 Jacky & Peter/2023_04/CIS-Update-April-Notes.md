
macros/cis/CIS_DB_Update.py --date 'A' 'B' --ldate 448575 448776 448850 449201 449640 450171 450206 450464 450488 450567 451018

Excluded runs due to bad AmpQ-Charge: 448828, 450805 
LBA14 excluded runs (make sure to check puls shae and fit there): 448420, 448427
Exclude due to large DB deviation errors: 449942
macros/cis/Public_Super_Macro.py --gcals --date '04/01/23' '05/01/23' --listdate 448575 448776 448850 449201 449640 449942 450171 450206 450464 450488 450567 451018 --datelabel 'April 1 - May 1, 2023' --mean --lowmem --rmsplots --flagplots



macros/cis/Super_Public_Macro.py --history -0.5 0.5 --date 'A' 'B' --listdate 448575 --secondlistdate 451018 --datelabel 'April 1 v. May 1, 2023'

Analyze excluded LBA14 runs:
macros/cis/investigate.py --date 448420 --ldate 448420 --region LBA_m14 --usescans --all --verbose --pevent
