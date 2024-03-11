#!/bin/bash
#
# Read the raw RBR Quartz3 data files from the Pioneer MAB Surface Moorings and
# create parsed datasets available in JSON formatted files for further
# processing and review.
#
# P. Whelan 2023-11-13 -- Original code
# C. Wingard 2024-03-08 -- Updated to use the harvest_options.sh script to
#                          parse the command line inputs

# include the help function and parse the required and optional command line options
DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
source "$DIR/harvest_options.sh"

# Parse the file
if [ -e "$IN" ]; then
    cd /home/ooiuser/code/cgsn-parsers || exit
    python -m cgsn_parsers.parsers.parse_rbrq3 -i "$IN" -o "$OUT" || echo "ERROR: Failed to parse $IN"
fi
