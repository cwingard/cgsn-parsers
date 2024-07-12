#!/bin/bash
# harvest_vemco.sh
#
# Reads the raw Vemco VR2C data files from the Endurance and Pioneer Coastal
# Surface Moorings and create parsed datasets available in JSON formatted files
# for # further processing and review.
#
# C. Wingard 2024-07-10 -- Original code

# include the help function and parse the required and optional command line options
DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
source "$DIR/harvest_options.sh"

# Parse the file
if [ -e "$IN_FILE" ]; then
    cd /home/ooiuser/code/cgsn-parsers || exit
    python -m cgsn_parsers.parsers.parse_vemco -i "$IN_FILE" -o "$OUT_FILE" || echo "ERROR: Failed to parse $IN_FILE"
fi
