#!/bin/bash                                                                                                                                                   
if [ -z $ATLAS_RELEASE_BASE ]; then
    echo
    echo "Setting up ATLAS"
    echo

    ATRELEASE=22.0.17
    TESTAREA=${PWD}
    cd $TESTAREA/

    setupATLAS
    asetup $ATRELEASE,Athena,here

    TUCSPATH=$TESTAREA
    cd $TUCSPATH
    TUCSRESULTS=$TUCSPATH

fi
