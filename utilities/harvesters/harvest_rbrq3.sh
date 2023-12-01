#!/bin/bash
#
# Read the raw RBR Quartz3 data files from the Pioneer MAB Surface Moorings and create
# parsed datasets available in JSON formatted files for further processing and
# review.
#
# P. Whelan  2023-11-13

# Parse the command line inputs
if [ $# -ne 6 ]; then
    echo "$0: required inputs are the platform and deployment names, the DCL number, the RBRQ3 "
    echo "directory name, the subassembly [buoy/nsif/mfn] location of the RBRQ3 and the name"
    echo "of the file to process."
    echo "     example: $0 cp11cnsm D00001 dcl16 presf nsif 20240505.presf.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
DCL=${3,,}
PRESF=${4,,}
SUBASY=${5,,}
FILE=`basename $6`

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/parsed"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$DCL/$PRESF/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/$SUBASY/presf/${FILE%.log}.json"
if [ ! -d `dirname $OUT` ]; then
    mkdir -p `dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    cd /home/ooiuser/code/cgsn-parsers
    python -m cgsn_parsers.parsers.parse_rbrq3 -i $IN -o $OUT
fi
