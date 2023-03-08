#!/bin/bash

# Contact: rute.pedro@cern.ch
# runtable20xx.csv come from data summary page:
# https://atlas.web.cern.ch/Atlas/GROUPS/DATAPREPARATION/DataSummary/2015/runsum.py?style=table
#
# For Run2 the only place where you need to touch is year (in principle...)

year="2015"

infile="data/runtable"$year".csv"
outfile="data/deliveredLumiTime"$year

echo
head -2  $infile | cut -c -150
tail -10 $infile | cut -c -150 | sort
echo

# produce txt file with date and luminosity (converts date to UNIX format) 
more $infile | grep -v VdM | sort > tmp1
awk -F, '/[0-9],/{di=substr($6,2,14); "date -d 20\""di"\" +%s"| getline ti; print ti," 0.0"}' tmp1 > tmp #Lumi at start of the run is 0.0
awk -F, '/[0-9],/{df=substr($7,2,14); "date -d 20\""df"\" +%s"| getline tf; print tf,$12}' tmp1 >> tmp
more tmp | grep -v % | sort > $outfile.txt

echo
head -10 $outfile.txt
echo

# produce root file with luminosity graphs: $outfile.root
python root_macros/mk-lumi-vs-time.py $outfile

# clean up
rm -f tmp* $outfile.txt


