#!/bin/bash
#
# Read the raw OPTAA data files from the Endurance Surface Moorings and create
# parsed datasets available in JSON formatted files for further processing and
# review.
#
# R. Desiderio. 2015-12-17

# Parse the command line inputs
if [ $# -ne 6 ]; then
    echo "$0: required inputs are the platform and deployment names, the DCL number, the OPTAA"
    echo "directory name, the subassembly [buoy/nsif/mfn] location of the OPTAA and the name"
    echo "of the file to process."
    echo "     example: $0 ce01issm D00001 dcl16 optaa1 nsif 20150505_233000.optaa1.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
DCL=${3,,}
OPTAA=${4,,}
SUBASY=${5,,}
FILE=`/bin/basename $6`

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/proc"
PYTHON="/home/ooiuser/bin/conda/bin/python3"

IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$DCL/$OPTAA/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/$SUBASY/optaa/${FILE%.log}.json"
if [ ! -d `/usr/bin/dirname $OUT` ]; then
    mkdir -p `/usr/bin/dirname $OUT`
fi

# Parse the file
if [ ! -e $OUT ]; then
    cd /home/ooiuser/code/cgsn-parsers
    $PYTHON -m cgsn_parsers.parsers.parse_optaa -i $IN -o $OUT
fi
