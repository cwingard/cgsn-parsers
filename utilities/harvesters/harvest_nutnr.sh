#!/bin/bash
# harvest_nutnr.sh
#
# Reads the raw NUTNR data files from the Endurance and Pioneer Surface Moorings
# and create parsed datasets available in JSON formatted files for further
# processing and review.
#
# C. Wingard 2015-04-17 -- Original code
# C. Wingard 2024-03-08 -- Updated to use the harvest_options.sh script to
#                          parse the command line inputs

# include the help function and parse the required and optional command line options
DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
source "$DIR/harvest_options.sh"

# check the processing flag for the correct NUTNR data set type (suna, isus, isus_condensed)
case $FLAG in
    "suna" | "isus" | "isus_condensed" )
        ;;
    * )
        echo "ERROR: Incorrect NUTNR data set type, $FLAG, in the processing"
        echo "flag. Please specify either suna, isus or isus_condensed (case-insensitive)"
        echo "for the instrument type with the -f option."
        exit 1 # exit and indicate error
        ;;
esac

# Parse the file
if [ -e "$IN_FILE" ]; then
    cd /home/ooiuser/code/cgsn-parsers || exit
    python -m cgsn_parsers.parsers.parse_nutnr -i "$IN_FILE" -o "$OUT_FILE" -s $FLAG || echo "ERROR: Failed to parse $IN_FILE"
fi
