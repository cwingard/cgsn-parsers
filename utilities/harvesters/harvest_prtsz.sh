#!/bin/bash
#
# Read the raw PRTSZ data files from the Pioneer MAB Surface Moorings and create
# parsed datasets available in JSON formatted files for further processing and
# review.
#
# S. Dahlberg  2024-02-12

# Parse the command line inputs
if [ $# -ne 6 ]; then
    echo "$0: required inputs are the platform and deployment names, the DCL number, the PRTSZ "
    echo "directory name, the subassembly [buoy/nsif/mfn] location of the PRTSZ and the name"
    echo "of the file to process."
    echo "     example: $0 cp11cnsm D00001 dcl16 prtsz nsif 20240505.prtsz.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
DCL=${3,,}
PRTSZ=${4,,}
SUBASY=${5,,}
FILE=`basename $6`

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/parsed"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$DCL/$PRTSZ/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/$SUBASY/prtsz/${FILE%.log}.json"
if [ ! -d `dirname $OUT` ]; then
    mkdir -p `dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    cd /home/ooiuser/code/cgsn-parsers
    python -m cgsn_parsers.parsers.parse_prtsz -i $IN -o $OUT
fi
