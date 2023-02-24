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
    echo "the subassembly [buoy/nsif/mfn] location of the CPM, a flag to indicate if"
    echo "the data is coming from the superv (0) or syslog (1), and the name of the file"
    echo "to process."
    echo ""
    echo "     example: $0 ce01issm D00001 cpm1 buoy 0 20150505.superv.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
CPM=${3,,}
SUBASY=${4,,}
FLAG=$5
FILE=`basename $6`

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/parsed"

# based on the switch flag, use either the supervisor data or the syslog.
if [ $FLAG == 0 ]; then
    SUPER="superv"
else
    SUPER="syslog"
fi

# Setup the input and output file names as well as the absolute paths
if [ $CPM = "cpm1" ]; then
    IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$SUPER/$FILE"
else
    IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$CPM/$SUPER/$FILE"
fi
OUT="$PARSED/$PLATFORM/$DEPLOY/$SUBASY/superv/$CPM/${FILE%.log}.json"
if [ ! -d `dirname $OUT` ]; then
    mkdir -p `dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    cd /home/ooiuser/code/cgsn-parsers
    python -m cgsn_parsers.parsers.parse_superv_cpm -i $IN -o $OUT
fi
