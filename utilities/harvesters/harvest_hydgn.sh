#!/bin/bash
#
# Read the raw hydrogen data files for the Endurance Coastal Surface Moorings
# and create parsed datasets available in JSON formatted files for further
# processing and review.
#
# Wingard, C. 2015-04-17

# Parse the command line inputs
if [ $# -ne 5 ]; then
    echo "$0: required inputs are the platform and deployment names, the DCL"
    echo "name, the hydrogen sensor name and the name of the file to process."
    echo "     example: $0 ce02shsm D00001 dcl11 hyd1 20150505.hyd1.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
DCL=${3,,}
HYD=${4,,}
FILE=`basename $5`

HYD_NUM=${HYD%%#0_*}

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/parsed"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$DCL/$HYD/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/buoy/hyd-$HYD_NUM/${FILE%.log}.json"
if [ ! -d `dirname $OUT` ]; then
    mkdir -p `dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    cd /home/ooiuser/code/cgsn-parsers
    python -m cgsn_parsers.parsers.parse_hydgn -i $IN -o $OUT
fi
