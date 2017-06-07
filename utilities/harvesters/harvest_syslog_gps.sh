#!/bin/bash
#
# Read the GPS data from the syslog files for the Profiler Moorings and create
# parsed datasets available in JSON formatted files for further processing and review.
#
# Wingard, C. 2017-04-05

# Parse the command line inputs
if [ $# -ne 3 ]; then
    echo "$0: required inputs are the platform and deployment names,"
    echo "the name of the DCL, and the name of the file to process."
    echo "     example: $0 ce09ospm D00006 20161003.syslog.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
FILE=`/bin/basename $3`

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/proc"
PYTHON="/home/ooiuser/bin/conda/bin/python3"

if [ -z "${PLATFORM/*pm*}" ]; then
    # path is different for profiler moorings
    IN="$RAW/$PLATFORM/$DEPLOY/syslog/$FILE"
else
    IN="$RAW/$PLATFORM/$DEPLOY/cg_data/syslog/$FILE"
fi
OUT="$PARSED/$PLATFORM/$DEPLOY/buoy/gps/${FILE%.log}.json"
if [ ! -d `/usr/bin/dirname $OUT` ]; then
    mkdir -p `/usr/bin/dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    cd /home/ooiuser/code/cgsn-parsers
    $PYTHON -m cgsn_parsers.parsers.parse_syslog_gps -i $IN -o $OUT
fi
