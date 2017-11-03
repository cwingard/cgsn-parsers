#!/bin/bash
#
# Read the raw MOPAK (aka 3DMGX3) data files from the Profiler Moorings and create
# parsed datasets available in JSON formatted files for further processing and review.
#
# C. Wingard  2016-02-27

# Parse the command line inputs
if [ $# -ne 3 ]; then
    echo "$0: required inputs are the platform and deployment names, and the name of the file to process."
    echo "     example: $0 ce09ospm D00006 20161004_114542.3dmgx3.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
FILE=`basename $3`
RAW=`dirname $3`

# Set the default directory paths
PARSED="/home/ooiuser/data/proc"

# Setup the input and output filenames as well as the absolute paths
OUT="$PARSED/$PLATFORM/$DEPLOY/buoy/3dmgx3/${FILE%.log}.json"
if [ ! -d `dirname $OUT` ]; then
    mkdir -p `dirname $OUT`
fi

# Parse the file
if [ ! -e $OUT ]; then
    cd /home/ooiuser/code/cgsn-parsers
    python -m cgsn_parsers.parsers.parse_mopak -i $RAW/$FILE -o $OUT
fi
