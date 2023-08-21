#!/bin/bash
#
# Read the raw FLORT data files from the Endurance Surface Moorings and create
# parsed datasets available in JSON formatted files for further processing and
# review.
#
# C. Wingard  2016-02-19

# Parse the command line inputs
if [ $# -ne 6 ]; then
    echo "$0: required inputs are the platform and deployment names, the DCL number, the FLORT "
    echo "directory name, the subassembly [buoy/nsif/mfn] location of the FLORT and the name"
    echo "of the file to process."
    echo "     example: $0 ce01issm D00001 dcl16 flort nsif 20150505.flort.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
DCL=${3,,}
FLORT=${4,,}
SUBASY=${5,,}
FILE=`basename $6`

if [[ $FILE =~ flort([0-9]+)_ ]]; then
    FLORT_NUM="${BASH_REMATCH[1]}"
    FLORT_NUM=${FLORT_NUM##+(0)}
else
    FLORT_NUM="1"
fi

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/parsed"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$DCL/$FLORT/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/$SUBASY/flort-$FLORT_NUM/${FILE%.log}.json"
if [ ! -d `dirname $OUT` ]; then
    mkdir -p `dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    cd /home/ooiuser/code/cgsn-parsers
    python -m cgsn_parsers.parsers.parse_flort -i $IN -o $OUT
fi
