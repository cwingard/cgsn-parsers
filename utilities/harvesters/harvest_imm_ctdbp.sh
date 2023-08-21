#!/bin/bash
#
# Read the raw CTDBP data files (telemetered via the inductive modem) from the Global Surface Moorings and create
# parsed datasets available in JSON formatted files for further processing and review.
#
# C. Wingard  2017-07-19

# Parse the command line inputs
if [ $# -ne 3 ]; then
    echo "$0: required inputs are the platform and deployment names, and the path and name of the file to process."
    echo "     example: $0 gi01sumo D00003 ctdbp01_20160723_161810.DAT"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
FILE=`basename $3`
RAW=`dirname $3`
CTDBP=`basename $RAW`

if [[ $FILE =~ ctdbp([0-9]+)_ ]]; then
    CTDBP_NUM="${BASH_REMATCH[1]}"
    CTDBP_NUM=${CTDBP_NUM##+(0)}
else
    CTDBP_NUM="1"
fi

CTDBP="imm-ctdbp-${CTDBP_NUM}"

# Set the default directory paths
PARSED="/home/ooiuser/data/parsed"

# Setup the input and output filenames as well as the absolute paths
OUT="$PARSED/$PLATFORM/$DEPLOY/imm/$CTDBP/${FILE%.DAT}.json"
if [ ! -d `dirname $OUT` ]; then
    mkdir -p `dirname $OUT`
fi

# Parse the file, if hasn't already been parsed
if [ ! -e $OUT/ ]; then
    cd /home/ooiuser/code/cgsn-parsers
    python -m cgsn_parsers.parsers.parse_imm_ctdbp -i $RAW/$FILE -o $OUT
fi
