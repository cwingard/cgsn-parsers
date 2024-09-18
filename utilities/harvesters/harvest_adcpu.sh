#!/bin/bash
# harvest_adcp.sh
#
# Read the raw ADCPU data files for the Surface Moorings and create parsed datasets in JSON format
# for further processing and review.
#
# P. Whelan  2024-09-18 -- Copied fromharvest_adcp.sh

# include the help function and parse the required and optional command line options

DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
source "$DIR/harvest_options.sh"

# Parse the file
if [ -e "$IN_FILE" ]; then
    cd /home/ooiuser/code/cgsn-parsers || exit
    python -m cgsn_parsers.parsers.parse_adcpu -i "$IN_FILE" -o "$OUT_FILE" || echo "ERROR: Failed to parse $IN_FILE"
fi
