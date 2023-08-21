#!/bin/bash
#
# Read the raw GPS log files for the Endurance Surface Moorings and create
# parsed datasets available in JSON formatted files for further processing and
# review.
#
# Wingard, C. 2015-04-17

# Parse the command line inputs
if [ $# -ne 3 ]; then
    echo "$0: required inputs are the platform and deployment names,"
    echo "in that order, and the name of the file to process."
    echo "     example: $0 ce01issm D00001 20150505.gps.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
FILE=`basename $3`

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/parsed"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/cg_data/gps/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/buoy/gps-1/${FILE%.log}.json"
if [ ! -d `dirname $OUT` ]; then
    mkdir -p `dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    cd /home/ooiuser/code/cgsn-parsers
    python -m cgsn_parsers.parsers.parse_gps -i $IN -o $OUT
fi
