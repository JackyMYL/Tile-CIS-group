#!/bin/bash

ATRELEASE=22.0.68
AtlasSetup=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/x86_64/AtlasSetup/current/AtlasSetup

TESTAREA=/afs/cern.ch/user/h/hwilkens

cd $TESTAREA/

source $AtlasSetup/scripts/asetup.sh $ATRELEASE,Athena,here

TUCSPATH=$TESTAREA/Tucs
cd $TUCSPATH

WEBDIR=/afs/cern.ch/user/h/hwilkens/www/Tucs/plots/latest
mkdir -p  $WEBDIR/.
mkdir -p logs


rsync -avz /afs/cern.ch/user/t/tilecali/w0/ntuples/las /data/ntuples

echo '#######################'
echo '# Archiving old plots #'
echo '#######################'

#mkdir -p /data/plots
rm -f $TUCSPATH/plots/latest/*eps

echo '#################'
echo '# Starting TUCS #'
echo '#################'



NOW=`date "+%Y%m%d-%H%M%S"`

macros/laser/laser_DQ-twofilters-run3.py --pisa --date=2022-01-01 --filter=8 
# > logs/tucs$NOW.log 2> logs/tucs$NOW.err
#&
# MACROPID=$!
# A=0
# while [[ $A == 0 ]]; do 
#     ps v --pid=$MACROPID 
#     A=$?
#     sleep 1
# done | grep python > logs/memusage$NOW.log

echo '###################'
echo '# Generating pdfs #'
echo '###################'

if [ $? == 0 ]; then

    cd $TUCSPATH/plots/latest

    for part in EBA LBA LBC EBC ; do 
		cp new${part}.pdf  $WEBDIR/${part}_combined.pdf 
    done

    for cylinder in EBA EBC LB ;do 
	cp ${cylinder}_fibre_history.pdf $WEBDIR/${cylinder}_fibre_history_combined.pdf
    done



fi

cd $TUCSPATH

mkdir -p  /afs/cern.ch/user/h/hwilkens/www/Tucs/plots/latest/.
rm /afs/cern.ch/user/h/hwilkens/www/Tucs/plots/latest/*-combined.pdf

cp plots/latest/*-combined.pdf /afs/cern.ch/user/h/hwilkens/www/Tucs/plots/latest/.


