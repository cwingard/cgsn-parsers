#!/bin/bash
# harvest_vel3d.sh
#
# Reads the raw VEL3D data files from the Endurance and Pioneer Surface
# Moorings and create parsed datasets available in JSON formatted files for
# further processing and review.
#
# C. Wingard  2016-02-26
# C. Wingard 2024-03-08 -- Updated to use the harvest_options.sh script to
#                          parse the command line inputs

# include the help function and parse the required and optional command line options
DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
source "$DIR/harvest_options.sh"

# check the processing flag for the correct instrument sample rate (default is 8 Hz)
case $FLAG in
    4 | 8 | 16)
        ;;
    * )
        echo "ERROR: Incorrect Vector sampling rate $FLAG in the processing flag. Please"
        echo "specify either 4, 8, or 16 Hz for the sample rate with the  -f option."
        exit 1 # exit and indicate error
        ;;
esac

# Parse the file
if [ -e "$IN_FILE" ]; then
    cd /home/ooiuser/code/cgsn-parsers || exit
    python -m cgsn_parsers.parsers.parse_vel3d --i "$IN_FILE" -o "$OUT_FILE" -s $FLAG || echo "ERROR: Failed to parse $IN_FILE"
fi
