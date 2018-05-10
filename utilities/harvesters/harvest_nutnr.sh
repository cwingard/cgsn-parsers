#!/bin/bash
#
# Read the raw NUTNR data files for the Endurance Surface Moorings and create
# parsed datasets available in JSON formatted files for further processing and
# review.
#
# Wingard, C. 2015-04-17

# Parse the command line inputs
if [ $# -ne 7 ]; then
    echo "$0: required inputs are the platform and deployment names, the DCL number, the NUTNR"
    echo "directory name, the subassembly [buoy/nsif/mfn] location of the NUTNR, a switch to"
    echo "indicate what data is available (condensed or full) in the data files, and the name "
    echo "of the file to process."
    echo "     example: $0 ce01issm D00001 dcl16 nutnr nsif isus_condensed 20150505.nutnr.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
DCL=${3,,}
NUTNR=${4,,}
SUBASY=${5,,}
SWITCH=$6
FILE=`basename $7`

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/proc"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$DCL/$NUTNR/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/$SUBASY/$NUTNR/${FILE%.log}.json"
if [ ! -d `dirname $OUT` ]; then
    mkdir -p `dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    cd /home/ooiuser/code/cgsn-parsers
    python -m cgsn_parsers.parsers.parse_nutnr -i $IN -o $OUT -s $SWITCH
fi
