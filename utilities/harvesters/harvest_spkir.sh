#!/bin/bash
#
# Read the raw SPKIR data files from the Endurance Surface Moorings and create
# parsed datasets available in JSON formatted files for further processing and
# review.
#
# C. Wingard  2016-02-29

# Parse the command line inputs
if [ $# -ne 6 ]; then
    echo "$0: required inputs are the platform and deployment names, the DCL number, the SPKIR"
    echo "directory name, the subassembly [buoy/nsif/mfn] location of the SPKIR and the name"
    echo "of the file to process."
    echo "     example: $0 ce01issm D00001 dcl16 spkir nsif 20150505_233000.spkir.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
DCL=${3,,}
SPKIR=${4,,}
SUBASY=${5,,}
FILE=`basename $6`

SPKIR_NUM=${SPKIR%%_*}${SPKIR%%_*#0}


# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/parsed"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$DCL/$SPKIR/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/$SUBASY/spkir-$SPKIR_NUM/${FILE%.log}.json"
if [ ! -d `dirname $OUT` ]; then
    mkdir -p `dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    cd /home/ooiuser/code/cgsn-parsers
    python -m cgsn_parsers.parsers.parse_spkir -i $IN -o $OUT
fi
