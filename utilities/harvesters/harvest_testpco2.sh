#!/bin/bash
#
# Read the pCO2 test data files from the Surface Mooring and create parsed
# datasets available in JSON formatted files for further processing and
# review.
#
# Wingard, C. 2024-02-19

# Parse the command line inputs
if [ $# -ne 6 ]; then
    echo "$0: required inputs are the platform and deployment names, the DCL number, the sensor name,"
    echo "the subassembly [buoy/nsif/mfn] location of the sensor, and the name of the file to process."
    echo "     example: $0 ce02shsm D00018 dcl26 pco2test nsif 20240219.pco2test.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
DCL=${3,,}
PCO2TEST=${4,,}
SUBASY=${5,,}
FILE=$(basename $6)

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/parsed"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$DCL/$PCO2TEST/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/$SUBASY/$PCO2TEST/${FILE%.log}.json"
if [ ! -d $(dirname $OUT) ]; then
    mkdir -p $(dirname $OUT)
fi

# Parse the file
if [ -e $IN ]; then
    cd /home/ooiuser/code/cgsn-parsers || exit
    python -m cgsn_parsers.parsers.parse_testpco2 -i $IN -o $OUT || echo "Parsing failed for $IN"
fi
