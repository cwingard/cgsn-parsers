#!/bin/bash
#
# Read the raw TURBD data files from the MAB Test Surface Mooring and create
# parsed datasets available in JSON formatted files for further processing and
# review.
#
# C. Wingard  2023-03-03

# Parse the command line inputs
if [ $# -ne 6 ]; then
    echo "$0: required inputs are the platform and deployment names, the DCL number, the TURBD "
    echo "directory name, the subassembly [buoy/nsif/mfn] location of the TURBD and the name"
    echo "of the file to process."
    echo "     example: $0 as03cpsm D0001 dcl16 turbid nsif 20230303.turbid.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
DCL=${3,,}
TURBD=${4,,}
SUBASY=${5,,}
FILE=`basename $6`

TURBD_NUM=${TURBD%%_*}${TURBD%%_*#0}

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/parsed"

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$DCL/$TURBD/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/$SUBASY/turbd-$TURBD_NUM/${FILE%.log}.json"
if [ ! -d `dirname $OUT` ]; then
    mkdir -p `dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    cd /home/ooiuser/code/cgsn-parsers || exit
    python -m cgsn_parsers.parsers.parse_turbd -i $IN -o $OUT
fi
