#!/bin/bash
#
# Read the raw Power System log files for the Endurance Coastal Surface
# Moorings and create parsed datasets available in JSON formatted files
# for further processing and review.
#
# Wingard, C. 2015-04-17

# Parse the command line inputs
if [ $# -ne 4 ]; then
    echo "$0: required inputs are the platform and deployment names, a string indicating"
    echo "which type of power system [psc/mpea] is being parsed, and the name of the file to process."
    echo "     example: $0 ce07shsm D00005 psc 20150505.pwrsys.log"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
SWITCH=${3,,}
FILE=`basename $4`

# Set the default directory paths
RAW="/home/ooiuser/data/raw"
PARSED="/home/ooiuser/data/proc"

# Setup the input and output filenames as well as the absolute paths
case $SWITCH in
    "psc" )
        IN="$RAW/$PLATFORM/$DEPLOY/cg_data/pwrsys/$FILE"
        OUT="$PARSED/$PLATFORM/$DEPLOY/buoy/pwrsys/${FILE%.log}.json" ;;
    "mpea" )
        IN="$RAW/$PLATFORM/$DEPLOY/cg_data/cpm3/pwrsys/$FILE"
        OUT="$PARSED/$PLATFORM/$DEPLOY/mfn/pwrsys/${FILE%.log}.json" ;;
    * )
        echo "Unknown platform, please check the name again"
        exit 0 ;;
esac
if [ ! -d `dirname $OUT` ]; then
    mkdir -p `dirname $OUT`
fi

# Parse the file
if [ -e $IN ]; then
    cd /home/ooiuser/code/cgsn-parsers
    python -m cgsn_parsers.parsers.parse_pwrsys -i $IN -o $OUT -s $SWITCH
fi
