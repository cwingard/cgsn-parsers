#!/bin/bash
# harvest_testph.sh
#
# Reads the raw Deep SeaPHox V2 data files from the Endurance and Pioneer
# Surface Moorings and create parsed datasets available in JSON formatted
# files for further processing and review.
#
# C. Wingard 2021-10-12 -- Original code
# C. Wingard 2024-03-08 -- Updated to use the harvest_options.sh script to
#                          parse the command line inputs

# include the help function and parse the required and optional command line options
DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
source "$DIR/harvest_options.sh"

# check the processing flag for the correct pH sensor type
case $FLAG in
    "idron" | "sphox" )
        ;;
    * )
        echo "ERROR: Incorrect pH sensor name $FLAG in the processing flag. Please"
        echo "specify either idron or sphox for the pH test sensor with the -f option."
        exit 1 # exit and indicate error
        ;;
esac

# Parse the file
if [ -e "$IN_FILE" ]; then
    cd /home/ooiuser/code/cgsn-parsers || exit
    python -m cgsn_parsers.parsers.parse_testph -i "$IN_FILE" -o "$OUT_FILE" -s $FLAG || echo "ERROR: Failed to parse $IN_FILE"
fi
