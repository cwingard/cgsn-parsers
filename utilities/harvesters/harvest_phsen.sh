#!/bin/bash
# harvest_phsen.sh
#
# Reads the raw PHSEN data files from the Endurance and Pioneer Coastal Surface
# Moorings and create parsed datasets available in JSON formatted files for
# further processing and review.
#
# C. Wingard 2016-02-11 -- Original code
# C. Wingard 2024-03-08 -- Updated to use the harvest_options.sh script to
#                          parse the command line inputs

# include the help function and parse the required and optional command line options
DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
source "$DIR/harvest_options.sh"

# Parse the file
if [ -e "$IN" ]; then
    cd /home/ooiuser/code/cgsn-parsers || exit
    python -m cgsn_parsers.parsers.parse_phsen -i "$IN" -o "$OUT" || echo "ERROR: Failed to parse $IN"
fi
