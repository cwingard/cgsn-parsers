#!/bin/bash
#
# Read the raw PCO2W data files from the Endurance Coastal Surface Moorings and
# create parsed datasets available in JSON formatted files for further
# processing and review.
#
# C. Wingard  2016-02-19

# Parse the command line inputs
if [ $# -ne 6 ]; then
    echo "$0: required inputs are the platform and deployment names, the DCL"
    echo "number, the PCO2W directory name, the platform location of the PCO2W"
    echo "and the name of the file to process."
    echo "     example: $0 ce01issm D00001 dcl16 pco2w1 nsif 20150505.pco2w1.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
DCL=${3,,}
PCO2W=${4,,}
PLTFRM=${5,,}
FILE=`/bin/basename $6`

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/proc"
PYTHON="/home/ooiuser/bin/conda/bin/python3"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$DCL/$PCO2W/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/$PLTFRM/pco2w/${FILE%.log}.json"
if [ ! -d `/usr/bin/dirname $OUT` ]; then
    mkdir -p `/usr/bin/dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    cd /home/ooiuser/code/cgsn-parsers
    $PYTHON -m cgsn_parsers.parsers.parse_pco2w -i $IN -o $OUT
fi
