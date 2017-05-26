#!/bin/bash
#
# Read the FB250 data from the syslog files for the Profiler Moorings and create
# parsed datasets available in JSON formatted files for further processing and review.
#
# Wingard, C. 2017-04-05

# Parse the command line inputs
if [ $# -ne 3 ]; then
    echo "$0: required inputs are the platform and deployment names,"
    echo "the name of the DCL, and the name of the file to process."
    echo "     example: $0 ce02shsm D00005 20170523.syslog.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
FILE=`/bin/basename $3`

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/proc"
PYTHON="/home/ooiuser/bin/conda/bin/python3"

IN="$RAW/$PLATFORM/$DEPLOY/syslog/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/buoy/irid/${FILE%.log}.json"
if [ ! -d `/usr/bin/dirname $OUT` ]; then
    mkdir -p `/usr/bin/dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    cd /home/ooiuser/code/cgsn-parsers
    $PYTHON -m cgsn_parsers.parsers.parse_syslog_fb250 -i $IN -o $OUT
fi
