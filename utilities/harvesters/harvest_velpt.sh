#!/bin/bash
#
# Read the raw VELPT data files from the Endurance Surface Moorings and create
# parsed datasets available in JSON formatted files for further processing and
# review.
#
# C. Wingard  2016-02-23

# Parse the command line inputs
if [ $# -ne 6 ]; then
    echo "$0: required inputs are the platform and deployment names, the DCL number, the VELPT "
    echo "directory name, the subassembly [buoy/nsif/mfn] location of the VELPT and the name"
    echo "of the file to process."
    echo "     example: $0 ce01issm D00001 dcl16 velpt2 nsif 20150505.velpt2.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
DCL=${3,,}
VELPT=${4,,}
SUBASY=${5,,}
FILE=`basename $6`

if [[ $FILE =~ velpt([0-9]+)_ ]]; then
    VELPT_NUM="${BASH_REMATCH[1]}"
    VELPT_NUM=${VELPT_NUM##+(0)}
else
    VELPT_NUM="1"
fi

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/parsed"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$DCL/$VELPT/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/$SUBASY/velpt-$VELPT_NUM/${FILE%.log}.json"
if [ ! -d `dirname $OUT` ]; then
    mkdir -p `dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    cd /home/ooiuser/code/cgsn-parsers
    python -m cgsn_parsers.parsers.parse_velpt -i $IN -o $OUT
fi
