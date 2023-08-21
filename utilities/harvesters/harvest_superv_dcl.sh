#!/bin/bash
#
# Read the DCL Supervisor log files for the Endurance Surface Moorings and
# create parsed datasets available in JSON formatted files for further
# processing and review.
#
# Wingard, C. 2015-04-17

# Parse the command line inputs
if [ $# -ne 6 ]; then
    echo "$0: required inputs are the platform and deployment names, the name of the DCL,"
    echo " the subassembly [buoy/nsif/mfn] location of the DCL, a flag to indicate if"
    echo "the data is coming from the superv (0) or syslog (1), and the name of the file"
    echo "to process."
    echo ""
    echo "     example: $0 ce02shsm D00001 dcl11 buoy 0 20150505.superv.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
DCL=${3,,}
SUBASY=${4,,}
FLAG=$5
FILE=`basename $6`

if [[ $FILE =~ dcl([0-9]+)_ ]]; then
    DCL_NUM="${BASH_REMATCH[1]}"
    DCL_NUM=${DCL_NUM##+(0)}
else
    DCL_NUM="1"
fi

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/parsed"

# based on the switch flag, use either the supervisor data or the syslog.
if [ $FLAG == 0 ]; then
    SUPER="superv"
else
    SUPER="syslog"
fi

# Setup the input and output filenames as well as the absolute paths
IN="$RAW/$PLATFORM/$DEPLOY/cg_data/$DCL/$SUPER/$FILE"
OUT="$PARSED/$PLATFORM/$DEPLOY/$SUBASY/superv/dcl-$DCL_NUM/${FILE%.log}.json"
if [ ! -d `dirname $OUT` ]; then
    mkdir -p `dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    cd /home/ooiuser/code/cgsn-parsers
    python -m cgsn_parsers.parsers.parse_superv_dcl -i $IN -o $OUT
fi
