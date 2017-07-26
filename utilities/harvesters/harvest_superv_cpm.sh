#!/bin/bash
#
# Read the CPM Supervisor log files for the Endurance Coastal Surface Moorings
# and create parsed datasets available in JSON formatted files for further
# processing and review.
#
# Wingard, C. 2015-04-17

# Parse the command line inputs
if [ $# -ne 6 ]; then
    echo "$0: required inputs are the platform and deployment names, the name of the CPM,"
    echo "the subassembly [buoy/nsif/mfn] location of the CPM, the directory base switch"
    echo "and the name of the file to process."
    echo "     example: $0 ce01issm D00001 cpm1 buoy 0 20150505.superv.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
CPM=${3,,}
SUBASY=${4,,}
BASE=$5
FILE=`/bin/basename $5`

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/proc"
PYTHON="/home/ooiuser/bin/conda/bin/python3"

# Setup the input and output filenames as well as the absolute paths
if [ $BASE == 0 ]; then
    IN="$RAW/$PLATFORM/$DEPLOY/cg_data/superv/$FILE"
else
    IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$CPM/superv/$FILE"
fi
OUT="$PARSED/$PLATFORM/$DEPLOY/$SUBASY/superv/$CPM/${FILE%.log}.json"
if [ ! -d `/usr/bin/dirname $OUT` ]; then
    mkdir -p `/usr/bin/dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    cd /home/ooiuser/code/cgsn-parsers
    $PYTHON -m cgsn_parsers.parsers.parse_superv_cpm -i $IN -o $OUT
fi
