#!/bin/bash
#
# Read the raw IFCB header data files from the Pioneer MAB Surface Moorings and
# create parsed datasets available in JSON formatted files for further 
# processing and review.
#
# P. Whelan 2024-09-18 -- Copied from harvest_ifcb.sh

# include the help function and parse the required and optional command line options
DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
source "$DIR/harvest_options.sh"

# Parse the file
if [ -e "$IN_FILE" ]; then
    cd /home/ooiuser/code/cgsn-parsers || exit
    python -m cgsn_parsers.parsers.parse_ifcb_adc -i "$IN_FILE" -o "$OUT_FILE" || echo "ERROR: Failed to parse $IN_FILE"
fi
