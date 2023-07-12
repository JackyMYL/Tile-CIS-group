#!/bin/bash

if [ -z $ATLAS_RELEASE_BASE ]; then 
    echo 
    echo "Setting up ATLAS" 
    echo
    ATRELEASE=21.0.17
    AtlasSetup=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/x86_64/AtlasSetup/current/AtlasSetup

    TESTAREA=/afs/cern.ch/user/h/hwilkens/

    cd $TESTAREA/

    source $AtlasSetup/scripts/asetup.sh $ATRELEASE,here

    TUCSPATH=$TESTAREA/Tucs
    cd $TUCSPATH
fi 

# The list of IOVs


function do_run {

    rm -r results/tileSqlite-${1}.db
    macros/laser/laser_autocalib.py --first $1 --IgnoreStatus
    ReadCalibFromCool.py --schema="sqlite://;schema=results/tileSqlite-"$1".db;dbname=CONDBR2" --tag='RUN2-HLT-UPD1-00' --folder=/TILE/OFL02/CALIB/LAS/LIN > run-$1.txt
    ln -sf run-$1.txt new_db.txt
    root -b -l root_macros/doChecksDiff.cc
}

ReadBchFromCool.py --run=99999999  --tag=UPD4 | grep "BAD" | awk '{ print $1" "$2" "$3 }' >> masked.txt
ReadCalibFromCool.py --folder=/TILE/OFL02/CALIB/LAS/LIN --tag='RUN2-HLT-UPD1-00' | grep -v " 1    " >> Laser_DB.txt

LIST=`mysql -h pcata007.cern.ch -u reader -NB -e "select run from tile.comminfo where date>'2018-05-07' and lasreqamp='15000' and lasfilter='8' and type='Las' and not (recofrags like '%%005%%' or recofrags like '%%50%%' ) and beamfrags like '%%200017%%' and not setup='ATLAS' and comments is NULL"`

echo $LIST

for run in $LIST ; do ##HG 2018
    if [ -d diff_plots-${run} ]; then
	echo ${run} already processed
	continue
    fi
    mkdir -p diff_plots
    do_run $run 
    mv diff_plots diff_plots-${run}     
    mv results/tileSqlite-${run}.db diff_plots-${run}/.
    mv results/output/Tucs.HIST.root results/output/Tucs.HIST.${run}.root
    cp run-${run}.txt diff_plots-${run}/.
    cp results/tile_laser_map${run}.pdf diff_plots-${run}/.
    cp -a diff_plots-${run} ${HOME}/www/Tucs/constants-${run}
done




