#/bin/bash 


NOW=`date "+%Y%m%d-%H%M%S"`
macros/laser/laser_stab_references.py --low=$1 --high=$2 --iov=248375 --region=MBTS
cp tileSqlite.db tileSqlite.db-$NOW-MBTS



