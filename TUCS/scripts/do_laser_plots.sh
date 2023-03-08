#!/bin/bash 

echo "Remaining disk space"
df | grep data
echo

ATRELEASE=22.0.68
AtlasSetup=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/x86_64/AtlasSetup/current/AtlasSetup

TESTAREA=/afs/cern.ch/user/h/hwilkens

cd $TESTAREA/

source $AtlasSetup/scripts/asetup.sh $ATRELEASE,Athena,here

TUCSPATH=$TESTAREA/Tucs

# function generate_pdf() {
#     OUTFILE=$1
#     shift 1
#     INPUT=$@
#     local LD_LIBRARY_PATH=""
# #    gs -dFIXEDMEDIA -sPAPERSIZE=a4 -dPSFitPage  -q -dSAFER -dNOPAUSE -dBATCH -sOutputFile=$OUTFILE -sDEVICE=pdfwrite -c .setpdfwrite -dFitPage $INPUT
# #    gs -dFIXEDMEDIA -sPAPERSIZE=a4 -dPSFitPage  -q -dSAFER -dNOPAUSE -dBATCH -sOutputFile=$OUTFILE -sDEVICE=pdfwrite -dDEVICEWIDTHPOINTS=842 -dDEVICEHEIGHTPOINTS=595 $INPUT
# #    gs -sDEVICE=pdfwrite -dNOPAUSE -dBATCH -dSAFER -sOutputFile=$OUTFILE -dNORANGEPAGESIZE  $INPUT > /dev/null
#     gs -sDEVICE=pdfwrite -dNOPAUSE -dBATCH -dSAFER -sOutputFile=$OUTFILE  $INPUT > /dev/null
# }

function generate_pdf() {
    OUTFILE=$1
    shift 1
    INPUT=$@
    local LD_LIBRARY_PATH=""
    gs -sDEVICE=pdfwrite -dNOPAUSE -dBATCH -dSAFER -dFIXEDMEDIA -dFitPage -sPAPERSIZE="(a4)"  -sOutputFile=$OUTFILE  $INPUT > /dev/null
}


function generate_pdf_from_eps() {
    OUTFILE=$1
    shift 1
    INPUT=$@
    local LD_LIBRARY_PATH=""

    cat $INPUT  | epstopdf --filter > $OUTFILE
}



cd $TUCSPATH

WEBDIR=/afs/cern.ch/user/h/hwilkens/www/Tucs/plots/latest
mkdir -p  $WEBDIR/.
mkdir -p logs

rsync -avz /afs/cern.ch/user/t/tilecali/w0/ntuples/las /data/ntuples

echo '#######################'
echo '# Archiving old plots #'
echo '#######################'

rm -f $TUCSPATH/plots/latest/0*eps

echo '#################'
echo '# Starting TUCS #'
echo '#################'

NOW=`date "+%Y%m%d-%H%M%S"`

#macros/laser/laser_DQ-twofilters-run2.py --region=LBA,LBC,EBC --pisa --date=2018-11-01 > logs/tucs$NOW.log 2> logs/tucs$NOW.err
#macros/laser/laser_DQ-twofilters-run2.py --pisa --date=2018-10-01 > logs/tucs$NOW.log 2> logs/tucs$NOW.err
macros/laser/laser_DQ-twofilters-run3.py --direct --date=2022-03-01 > logs/tucs$NOW.log 2> logs/tucs$NOW.err

if [ $? == 0 ]; then

    cd $TUCSPATH/plots/latest

    # for part in EBA LBA LBC EBC ; do
    # 	list=`ls ${part}[0-9][0-9]_history.ps `
    # 	if [[ ! -z "$list" ]]; then
    # 	    generate_pdf ${part}.pdf $list
    # 	fi
    # done

    cp diode_history.pdf $WEBDIR/diode_history_new.pdf 
    for part in EBA LBA LBC EBC ; do
	cp new${part}.pdf  $WEBDIR/${part}_direct.pdf 
    done

    cp global_history.pdf $WEBDIR/.
    for cylinder in EBA EBC LB ;do 
	cp ${cylinder}_fibre_history.pdf $WEBDIR/${cylinder}_fibre_history_direct.pdf
    done


#    generate_pdf FibreCorrections.pdf global_history.ps *_fiber_history.ps

#cat c*.eps | epstopdf --filter > BadChannels.pdf

#     LIST=`grep -l "ADC de" c*eps`
#     if [[ $LIST != "" ]]; then
# 	generate_pdf_from_eps ADCDead.pdf $LIST
#     fi

#     LIST=`grep -l "ADC mas" c*eps`
#     if [[ $LIST != "" ]]; then
# 	generate_pdf_from_eps ADCMasked.pdf $LIST
#     fi

#     LIST=`grep -l "Stuck" c*eps`
#     if [[ $LIST != "" ]]; then
# 	generate_pdf_from_eps StuckBit.pdf $LIST
#     fi

#     LIST=`grep -l "nnel mas" c*eps`
#     if [[ $LIST != "" ]]; then
# 	generate_pdf_from_eps ChannelMasked.pdf $LIST
#     fi

#     LIST=`grep -l "No P" c*eps`
#     if [[ $LIST != "" ]]; then
# 	generate_pdf_from_eps NoPMT.pdf $LIST
#     fi

#     LIST=`grep -l "Wrong HV" c*eps`
#     if [[ $LIST != "" ]]; then
# 	generate_pdf_from_eps WrongHV.pdf $LIST
#     fi

# # MBTS channels

     LIST=`pdfgrep -e 'E[5,6]' -l channel_EB???_pmt??_history.pdf`
     if [[ $LIST != "" ]]; then
 	pdfunite $LIST $WEBDIR/MBTS.pdf 
     fi

     LIST=`pdfgrep E1 -l channel_EB???_pmt13_history.pdf`
     if [[ $LIST != "" ]]; then
 	pdfunite $LIST $WEBDIR/E1.pdf 
     fi
     
     LIST=`pdfgrep E2 -l channel_EB???_pmt14_history.pdf`
     if [[ $LIST != "" ]]; then
 	pdfunite $LIST $WEBDIR/E2.pdf 
     fi

     LIST=`pdfgrep E3 -l channel_EB???_pmt01_history.pdf channel_EBC18_pmt19_history.pdf channel_EBA15_pmt19_history.pdf | sort`
     if [[ $LIST != "" ]]; then
 	pdfunite $LIST $WEBDIR/E3.pdf 
     fi

     LIST=`pdfgrep E4 -l channel_EB???_pmt02_history.pdf channel_EBC18_pmt20_history.pdf channel_EBA15_pmt20_history.pdf | sort`
     if [[ $LIST != "" ]]; then
 	pdfunite $LIST $WEBDIR/E4.pdf 
     fi

#     LIST=`grep "D4" -l channel*eps`
#     if [[ $LIST != "" ]]; then
# 	generate_pdf_from_eps D4.pdf $LIST
#     fi

#     LIST=`grep "C10" -l channel*eps`
#     if [[ $LIST != "" ]]; then
# 	generate_pdf_from_eps C10.pdf $LIST
#     fi
     cp channel_* ~/www/Tucs/plots/latest/channels/.     
#    cp c*.eps /afs/cern.ch/user/h/hwilkens/www/Tucs/plots/latest/.
else
    echo "laser_DQ failed"
fi


echo '#################'
echo '# Starting TUCS #'
echo '#################'
cd $TUCSPATH
NOW=`date "+%Y%m%d-%H%M%S"`
macros/laser/laser_DQ-Time.py  --date=2022-03-01 > logs/time$NOW.log 2> logs/time$NOW.err

if [ $? == 0 ]; then
    cd $TUCSPATH/plots/Time/latest

    generate_pdf Time.pdf Time_distributions.ps global_time.ps ?B*time.ps
    cp Time.pdf /afs/cern.ch/user/h/hwilkens/www/Tucs/plots/latest/.
else
    echo "laser_DQ-Time.py failed"
fi



cd $TUCSPATH



