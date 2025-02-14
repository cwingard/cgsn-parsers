#!/bin/bash
# harvest_presf_avg.sh
#
# Reads the averaged RBR-PRESF data files from the Endurance and Pioneer Coastal Surface
# Moorings and create parsed datasets available in JSON formatted files for
# further processing and review.
#
# M. Carloni 2025-02-14 -- Original code

# include the help function and parse the required and optional command line options
DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
source "$DIR/harvest_options.sh"

# Parse the file
if [ -e "$IN_FILE" ]; then
    cd /home/ooiuser/code/cgsn-parsers || exit
    python -m cgsn_parsers.parsers.parse_rbrpresf_avg -i "$IN_FILE" -o "$OUT_FILE" || echo "ERROR: Failed to parse $IN_FILE"
fi
