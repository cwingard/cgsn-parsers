#!/bin/bash
#
# Read the Xeos beacon data files from the Surface Moorings and create parsed
# datasets available in JSON formatted files for further processing and review.
#
# C. Wingard  2023-11-09

# Parse the command line inputs
if [ $# -ne 4 ]; then
    echo "$0: required inputs are the platform and deployment names, the beacon name"
    echo "(e.g., XEOS1), a flag to indicate if the beacon is subsurface (0), or mounted"
    echo "on the tower (1), and the name of the file with the IMEI number to process."
    echo "     example: $0 ce07shsm D00017 XEOS1 1 300434062471940.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
XEOS_NAME=${3,,}
SURFACE=$4
FILE=`basename $5`

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/parsed"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/cg_data/xeos_sbd/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/buoy/$XEOS_NAME/${FILE%.log}.json"
if [ ! -d `dirname $OUT` ]; then
    mkdir -p `dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    cd /home/ooiuser/code/cgsn-parsers
    python -m cgsn_parsers.parsers.parse_xeos -i $IN -o $OUT -s $SURFACE
fi
