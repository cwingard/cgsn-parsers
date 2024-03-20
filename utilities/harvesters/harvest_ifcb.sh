#!/bin/bash
#
# Read the raw IFCB header data files from the Pioneer MAB Surface Moorings and
# create parsed datasets available in JSON formatted files for further 
# processing and review.
#
# P. Whelan  2023-11-20

# Parse the command line inputs
if [ $# -ne 6 ]; then
    echo "$0: required inputs are the platform and deployment names, the DCL number, the RBRQ3 "
    echo "directory name, the subassembly [buoy/nsif/mfn] location of the IFCB and the name"
    echo "of the file to process."
    echo "     example: $0 cp11cnsm D00001 dcl16 plims nsif D20240505T122122_IFCB195.hdr"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
DCL=${3,,}
PLIMS=${4,,}
SUBASY=${5,,}
FILE=`basename $6`

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/parsed"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$DCL/$PLIMS/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/$SUBASY/plims/${FILE%.log}.json"
if [ ! -d `dirname $OUT` ]; then
    mkdir -p `dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    cd /home/ooiuser/code/cgsn-parsers
    python -m cgsn_parsers.parsers.parse_ifcb_hdr -i $IN -o $OUT
fi
