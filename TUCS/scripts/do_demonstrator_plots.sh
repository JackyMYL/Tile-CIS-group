#!/bin/bash 

ATRELEASE=22.0.36
ATRELEASE=22.0.68
AtlasSetup=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/x86_64/AtlasSetup/current/AtlasSetup

TESTAREA=/afs/cern.ch/user/h/hwilkens

cd $TESTAREA/

source $AtlasSetup/scripts/asetup.sh $ATRELEASE,Athena,here

TUCSPATH=$TESTAREA/Tucs

function generate_pdf() {
    OUTFILE=$1
    shift 1
    INPUT=$@
    local LD_LIBRARY_PATH=""
#    gs -dFIXEDMEDIA -sPAPERSIZE=a4 -dPSFitPage  -q -dSAFER -dNOPAUSE -dBATCH -sOutputFile=$OUTFILE -sDEVICE=pdfwrite -c .setpdfwrite -dFitPage $INPUT
#    gs -dFIXEDMEDIA -sPAPERSIZE=a4 -dPSFitPage  -q -dSAFER -dNOPAUSE -dBATCH -sOutputFile=$OUTFILE -sDEVICE=pdfwrite -dDEVICEWIDTHPOINTS=842 -dDEVICEHEIGHTPOINTS=595 $INPUT
    gs -sDEVICE=pdfwrite -dNOPAUSE -dBATCH -dSAFER -sOutputFile=$OUTFILE -dNORANGEPAGESIZE  $INPUT > /dev/null
}

function generate_pdf_from_eps() {
    OUTFILE=$1
    shift 1
    INPUT=$@
    local LD_LIBRARY_PATH=""

    cat $INPUT  | epstopdf --filter > $OUTFILE
}


cd $TUCSPATH

mkdir -p  /afs/cern.ch/user/h/hwilkens/www/Tucs/plots/demonstrator/.
mkdir -p logs

rsync -avz /afs/cern.ch/user/t/tilecali/w0/ntuples/las /data/ntuples

echo '#######################'
echo '# Archiving old plots #'
echo '#######################'

rm -f $TUCSPATH/plots/latest/*

echo '#################'
echo '# Starting TUCS #'
echo '#################'

NOW=`date "+%Y%m%d-%H%M%S"`

#macros/laser/laser_DQ-twofilters-run2.py --region=LBA,LBC,EBC --pisa --date=2018-11-01 > logs/tucs$NOW.log 2> logs/tucs$NOW.err
#macros/laser/laser_DQ-twofilters-run2.py --pisa --date=2018-10-01 > logs/tucs$NOW.log 2> logs/tucs$NOW.err
#macros/laser/laser_DQ-twofilters-run3.py --date=2021-05-12 > logs/tucs$NOW.log 2> logs/tucs$NOW.err
macros/laser/laser_DQ-twofilters-run3.py --direct --date=2022-01-01 > logs/tucs$NOW.log 2> logs/tucs$NOW.err

cd plots/latest
pdftk newLBA.pdf cat 14 output /afs/cern.ch/user/h/hwilkens/www/Tucs/plots/demonstrator/LBA14.pdf
pdftk newLBC.pdf cat 14 output /afs/cern.ch/user/h/hwilkens/www/Tucs/plots/demonstrator/LBC14.pdf
pdftk LB_fibre_history.pdf cat 27 28 output /afs/cern.ch/user/h/hwilkens/www/Tucs/plots/demonstrator/LB14-fibres.pdf
pdfunite c*LBA14*pdf /afs/cern.ch/user/h/hwilkens/www/Tucs/plots/demonstrator/Demo-channels.pdf


#generate_pdf /afs/cern.ch/user/h/hwilkens/www/Tucs/plots/demonstrator/Demo.pdf *LB?14*.ps *LB14*.ps
#generate_pdf_from_eps /afs/cern.ch/user/h/hwilkens/www/Tucs/plots/demonstrator/
cd $TUCSPATH
NOW=`date "+%Y%m%d-%H%M%S"`
macros/laser/laser_DQ-Time.py  --date=2022-03-01 > logs/time$NOW.log 2> logs/time$NOW.err

cd $TUCSPATH/plots/Time/latest

generate_pdf /afs/cern.ch/user/h/hwilkens/www/Tucs/plots/demonstrator/Demo-time.pdf *LB?14*ps 
                          
