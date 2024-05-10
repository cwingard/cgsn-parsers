#!/bin/bash
#
# Read the raw MMP Prawler data files from the MAB Shallow water moorings and create
# parsed datasets available in JSON formatted files for further processing and
# review.
#
# P. Whelan   5/8/2024

# Parse the command line inputs
if [ $# -ne 6 ]; then
    echo "$0: required inputs are the platform and deployment names, the DCL number, the prawler "
    echo "directory name, the subassembly [buoy/nsif/mfn] location of the imm and the name"
    echo "of the file to process."
    echo "     example: $0 cp12wesw D0001 dcl11 prkt imm prkt_20240502_130021.DAT"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
DCL=${3,,}
PRAWLER=${4,,}
SUBASY=${5,,}
FILE=`basename $6`

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/parsed"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/$SUBASY/$PRAWLER/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/$SUBASY/$PRAWLER/${FILE%.log}.json"
if [ ! -d `dirname $OUT` ]; then
    mkdir -p `dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    cd /home/ooiuser/code/cgsn-parsers || exit
    python -m cgsn_parsers.parsers.parse_mmp_prawler -i $IN -o $OUT
fi
