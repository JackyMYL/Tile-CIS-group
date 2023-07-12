#!/bin/bash
export AtlasSetup=/afs/cern.ch/atlas/software/dist/AtlasSetup
alias asetup='source $AtlasSetup/scripts/asetup.sh'
asetup 20.1.4,builds,here,slc6
export TUCS="$PWD/"
