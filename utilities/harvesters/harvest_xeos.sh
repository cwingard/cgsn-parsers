#!/bin/bash
#
# Read the Xeos beacon data files from the Surface Moorings and create parsed
# datasets available in JSON formatted files for further processing and review.
#
# C. Wingard  2023-11-09

# Parse the command line inputs
if [ $# -ne 6 ]; then
    echo "$0: required inputs are the platform and deployment names, the beacon name"
    echo "(e.g., XEOS1), a string to indicate if the beacon is on a surface mooring (SM)"
    echo "or profiler mooring (PM), a boolean to indicate if the beacon is subsurface (1)"
    echo "or mounted on the tower (0), and the name of the file with the IMEI number"
    echo "to process."
    echo "     example: $0 ce07shsm D00017 XEOS1 SM 0 300434062471940.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
XEOS_NAME=${3,,}
MOORING=${4^^}
SURFACE=$5
FILE=$(basename "$6")

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/parsed"

# Setup the input and output filenames as well as the absolute paths
case $MOORING in
    "SM" )
        IN="$RAW/$PLATFORM/$DEPLOY/cg_data/xeos_sbd/$FILE"
        ;;
    "PM" )
        IN="$RAW/$PLATFORM/$DEPLOY/xeos_sbd/$FILE"
        ;;
    * )
        echo "ERROR: Unknown mooring type $MOORING, please specify either SM or PM for a surface or profiler mooring type, respectively"
        exit 1 # terminate and indicate error
        ;;
esac
OUT="$PARSED/$PLATFORM/$DEPLOY/buoy/$XEOS_NAME/${FILE%.log}.json"
if [ ! -d "$(dirname "$OUT")" ]; then
    mkdir -p "$(dirname "$OUT")"
fi

# Parse the file
if [ -e "$IN" ]; then
    cd /home/ooiuser/code/cgsn-parsers || exit
    python -m cgsn_parsers.parsers.parse_xeos -i "$IN" -o "$OUT" -s "$SURFACE"
fi
