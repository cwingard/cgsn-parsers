#!/bin/bash
#
# Read the raw ADCP data files (telemetered via the inductive modem) from the Profiler Moorings and create
# parsed datasets available in JSON formatted files for further processing and review.
#
# C. Wingard  2017-05-23

# Parse the command line inputs
if [ $# -ne 3 ]; then
    echo "$0: required inputs are the platform and deployment names, and the path and name of the file to process."
    echo "     example: $0 cp02pmci D00007 adcpt_20160920_162306.DAT"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
FILE=`/bin/basename $3`
RAW=`/usr/bin/dirname $3`

# Set the default directory paths
PARSED="/home/ooiuser/data/proc"
PYTHON="/home/ooiuser/bin/conda/bin/python3"

# Setup the input and output filenames as well as the absolute paths
OUT="$PARSED/$PLATFORM/$DEPLOY/imm/adcp/${FILE%.DAT}.json"
if [ ! -d `/usr/bin/dirname $OUT` ]; then
    mkdir -p `/usr/bin/dirname $OUT`
fi

# Parse the file, if hasn't already been parsed
if [ ! -e $OUT/ ]; then
    cd /home/ooiuser/code/cgsn-parsers
    $PYTHON -m cgsn_parsers.parsers.parse_imm_adcp -i $RAW/$FILE -o $OUT
fi
