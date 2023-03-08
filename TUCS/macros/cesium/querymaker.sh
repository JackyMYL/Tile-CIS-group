#!/bin/bash
# This script produces an SQL query by parsing reconstructed cesuim data.
# It uses cs[runnumber].db files.
# 
# Author: Mikhail Makouski <makouski@cern.ch>
#
if [ "q$1" == "q" ]; 
  then echo "usage: querymaker.sh year"; 
  exit; 
fi  
echo "USE tile;" > query.sql
#echo "TRUNCATE TABLE runDescr;" >> query.sql
find /data/cs/$1/int -maxdepth 2 -name "cs*.db" -exec awk -f make_query.awk "{}" >> query.sql ";"
