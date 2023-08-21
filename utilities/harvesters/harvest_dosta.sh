#!/bin/bash
#
# Read the raw DOSTA data files from the Endurance Coastal Surface Moorings and
# create parsed datasets available in JSON formatted files for further
# processing and review.
#
# C. Wingard  2016-02-19

# Parse the command line inputs
if [ $# -ne 6 ]; then
    echo "$0: required inputs are the platform and deployment names, the DCL number, the DOSTA "
    echo "directory name, the subassembly [buoy/nsif/mfn] location of the DOSTA and the name"
    echo "of the file to process."
    echo "     example: $0 ce07shsm D00001 dcl27 dosta nsif 20150505.dosta.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
DCL=${3,,}
DOSTA=$4
SUBASY=${5,,}
FILE=`basename $6`

DOSTA_NUM=${DOSTA%%_*}
DOSTA_NUM=$(echo $DOSTA | cut -d_ -f1)
DOSTA_NUM=${DOSTA_NUM##+(0)}

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/parsed"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$DCL/$DOSTA/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/$SUBASY/dosta-$DOSTA_NUM/${FILE%.log}.json"
if [ ! -d `dirname $OUT` ]; then
    mkdir -p `dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    cd /home/ooiuser/code/cgsn-parsers
    python -m cgsn_parsers.parsers.parse_dosta -i $IN -o $OUT
fi
