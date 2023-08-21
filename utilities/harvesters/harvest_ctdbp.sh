#!/bin/bash
#
# Read the raw CTDBP data files for the Surface Moorings and create parsed datasets available in JSON formatted files
# for further processing and review.
#
# Wingard, C. 2015-04-17

# Parse the command line inputs
if [ $# -ne 7 ]; then
    echo "$0: required inputs are the platform and deployment names, the DCL number, the CTDBP name,"
    echo "the subassembly [buoy/nsif/mfn] location of the CTDBP, a switch to indicate what data"
    echo "is available in the data files [solo/dosta/flort], and the name of the file to process."
    echo "     example: $0 ce01issm D00009 dcl16 ctdbp1 nsif dosta 20180505.ctdbp1.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
DCL=${3,,}
CTDBP=${4,,}
SUBASY=${5,,}
SWITCH=${6,,}
FILE=`basename $7`

CTDBP_NUM=${CTDBP%%/*}

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/parsed"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$DCL/$CTDBP/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/$SUBASY/ctdbp-$CTDBP_NUM/${FILE%.log}.json"
if [ ! -d `dirname $OUT` ]; then
    mkdir -p `dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    cd /home/ooiuser/code/cgsn-parsers
    python -m cgsn_parsers.parsers.parse_ctdbp -i $IN -o $OUT -s $SWITCH
fi
