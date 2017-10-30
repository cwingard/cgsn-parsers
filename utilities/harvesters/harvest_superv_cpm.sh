#!/bin/bash
#
# Read the CPM Supervisor log files for the Endurance Coastal Surface Moorings
# and create parsed datasets available in JSON formatted files for further
# processing and review.
#
# Wingard, C. 2015-04-17

# Parse the command line inputs
if [ $# -ne 5 ]; then
    echo "$0: required inputs are the platform and deployment names, the name of the CPM,"
    echo "the subassembly [buoy/nsif/mfn] location of the CPM, and the name of the file"
    echo "to process."
    echo "     example: $0 ce01issm D00001 cpm1 buoy 20150505.superv.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
CPM=${3,,}
SUBASY=${4,,}
FILE=`/bin/basename $5`

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/proc"
PYTHON="/home/ooiuser/bin/conda/bin/python3"

# Setup the input and output file names as well as the absolute paths
if [ $CPM = "cpm1" ]; then
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
