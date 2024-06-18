#!/bin/bash
#
# Read the raw MMP Prawler data files from the MAB Shallow water moorings and create
# parsed datasets available in JSON formatted files for further processing and
# review.
#
# P. Whelan 2024-05-08 -- Original code
# C. Wingard 2024-03-08 -- Updated to use the harvest_options.sh script to
#                          parse the command line inputs

# include the help function and parse the required and optional command line options
DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
source "$DIR/harvest_options.sh"

# Parse the file
if [ -e "$IN_FILE" ]; then
    cd /home/ooiuser/code/cgsn-parsers || exit
    python -m cgsn_parsers.parsers.parse_mmp_prawler -i $IN_FILE -o $OUT_FILE || echo "ERROR: Failed to parse $IN_FILE"
fi
