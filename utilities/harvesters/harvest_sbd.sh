#!/bin/bash
#
# Read the supervisor SBD modem data files from the Surface Moorings and create
# parsed datasets available in JSON formatted files for further processing and
# review.
#
# C. Wingard  2023-11-09

# Parse the command line inputs
if [ $# -ne 5 ]; then
    echo "$0: required inputs are the platform and deployment names, the SBD modem name"
    echo "(e.g., SBD1), a string to indicate if this is coming from a CPM or STC, and the"
    echo "name of the file with the IMEI number to process."
    echo ""
    echo "     example: $0 ce07shsm D00017 SBD1 cpm 300234060756120.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
SBD_NAME=${3,,}
SUPERV=${4,,}
FILE=$(basename "$5")

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/parsed"

# Setup the input and output filenames as well as the absolute paths
case $SUPERV in
    "cpm" )
        IN="$RAW/$PLATFORM/$DEPLOY/cg_data/irid_sbd/$FILE"
        ;;
    "stc" )
        IN="$RAW/$PLATFORM/$DEPLOY/irid_sbd/$FILE"
        ;;
    * )
        echo "ERROR: Incorrect supervisor type $SUPERV. Please specify either cpm or stc for the supervisor type"
        exit 1 # exit and indicate error
        ;;
esac
OUT="$PARSED/$PLATFORM/$DEPLOY/buoy/$SBD_NAME/${FILE%.log}.json"
if [ ! -d "$(dirname "$OUT")" ]; then
    mkdir -p "$(dirname "$OUT")"
fi

# Parse the file
if [ -e "$IN" ]; then
    cd /home/ooiuser/code/cgsn-parsers || exit
    python -m cgsn_parsers.parsers.parse_sbd -i "$IN" -o "$OUT" -s "$SUPERV" || echo "ERROR: Failed to parse $IN"
fi
