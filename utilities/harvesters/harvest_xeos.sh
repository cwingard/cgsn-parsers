#!/bin/bash
# harvest_xeos.sh
#
# Reads the raw Xeos beacon data files from the Endurance and Pioneer Surface
# Moorings and create parsed datasets available in JSON formatted files for
# further processing and review.
#
# C. Wingard 2024-02-02 -- Original code

# include the help function and parse the required and optional command line options
DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
source "$DIR/harvest_options.sh"

# check the processing flag for the correct supervisor types
case $FLAG in
    0 | 1 )
        ;;
    * )
        echo "ERROR: Incorrect subsurface value $FLAG in the processing flag. Please"
        echo "specify either 0 or 1 for a beacon mounted on a buoy tower (0) or"
        echo "subsurface (1) via the -f option."
        exit 1 # exit and indicate error
        ;;
esac

# Parse the file
if [ -e "$IN_FILE" ]; then
    cd /home/ooiuser/code/cgsn-parsers || exit
    python -m cgsn_parsers.parsers.parse_xeos -i "$IN_FILE" -o "$OUT_FILE" -s "$FLAG" || echo "ERROR: Failed to parse $IN_FILE"
fi
