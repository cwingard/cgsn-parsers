#!/bin/bash
# harvest_sbd.sh
#
# Reads the raw SBD data files from the Endurance and Pioneer Surface Moorings
# and create parsed datasets available in JSON formatted files for further
# processing and review.
#
# C. Wingard 2024-02-02 -- Original code

# include the help function and parse the required and optional command line options
DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
source "$DIR/harvest_options.sh"

# check the processing flag for the correct supervisor types
case $FLAG in
    "cpm" | "stc" )
        ;;
    * )
        echo "ERROR: Incorrect supervisor type $FLAG in the processing flag. Please"
        echo "specify either cpm or stc for the supervisor type with the -f option."
        exit 1 # exit and indicate error
        ;;
esac

# Parse the file
if [ -e "$IN" ]; then
    cd /home/ooiuser/code/cgsn-parsers || exit
    python -m cgsn_parsers.parsers.parse_sbd -i "$IN" -o "$OUT" -s "$FLAG" || echo "ERROR: Failed to parse $IN"
fi
