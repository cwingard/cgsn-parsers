#!/bin/bash
#
# Read the raw ASIMET Sonic Wind (SWND) module data files from the Endurance
# Surface Moorings and create parsed datasets available in JSON formatted
# files for further processing and review.
#
# C. Wingard  2024-02-14

# Parse the command line inputs
if [ $# -ne 5 ]; then
    echo "$0: required inputs are the platform and deployment names, the DCL number, the SWND "
    echo "directory name and the name of the file to process."
    echo "     example: $0 ce01issm D00001 dcl12 metwnd 20240214.metwnd.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
DCL=${3,,}
SWND=${4,,}
FILE=$(basename $5)

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/parsed"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$DCL/$SWND/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/buoy/$SWND/${FILE%.log}.json"
if [ ! -d "$(dirname $OUT)" ]; then
    mkdir -p "$(dirname $OUT)"
fi

# Parse the file
if [ -e $IN ]; then
    cd /home/ooiuser/code/cgsn-parsers || exit
    python -m cgsn_parsers.parsers.parse_swnd -i $IN -o $OUT || echo "Failed to parse $IN"
fi
