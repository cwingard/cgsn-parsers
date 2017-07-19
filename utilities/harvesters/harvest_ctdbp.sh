#!/bin/bash
#
# Read the raw CTDBP data files for the Endurance Surface Moorings and create
# parsed datasets available in JSON formatted files for further processing and
# review.
#
# Wingard, C. 2015-04-17

# Parse the command line inputs
if [ $# -ne 7 ]; then
    echo "$0: required inputs are the platform and deployment names, the DCL"
    echo "number, the CTDBP name, a switch to indicate what data is available"
    echo "in the data files, and the name of the file to process."
    echo "     example: $0 ce01issm D00001 dcl16 ctdbp1 nsif 2 20150505.ctdbp1.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
DCL=${3,,}
CTDBP=${4,,}
PLTFRM=${5,,}
SWITCH=$6
FILE=`/bin/basename $7`

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/proc"
PYTHON="/home/ooiuser/bin/conda/bin/python3"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$DCL/$CTDBP/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/$PLTFRM/ctdbp/${FILE%.log}.json"
if [ ! -d `/usr/bin/dirname $OUT` ]; then
    mkdir -p `/usr/bin/dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    cd /home/ooiuser/code/cgsn-parsers
    $PYTHON -m cgsn_parsers.parsers.parse_ctdbp -i $IN -o $OUT -s $SWITCH
fi
