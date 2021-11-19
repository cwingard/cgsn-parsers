#!/bin/bash
#
# Read the raw pH test data files from the Surface Mooring and create parsed
# datasets available in JSON formatted files for further processing and
# review.
#
# Wingard, C. 2021-10-12

# Parse the command line inputs
if [ $# -ne 6 ]; then
    echo "$0: required inputs are the platform and deployment names, the DCL number, the pH sensor name,"
    echo "the subassembly [buoy/nsif/mfn] location of the pH sensor, and the name of the file to process."
    echo "     example: $0 ce02shsm D00013 dcl26 sphox nsif 20210926.sphox.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
DCL=${3,,}
PHTEST=${4,,}
SUBASY=${5,,}
FILE=`basename $6`

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/proc"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$DCL/$PHTEST/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/$SUBASY/$PHTEST/${FILE%.log}.json"
if [ ! -d `dirname $OUT` ]; then
    mkdir -p `dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    cd /home/ooiuser/code/cgsn-parsers
    python -m cgsn_parsers.parsers.parse_phtest -i $IN -o $OUT -s $PHTEST
fi
