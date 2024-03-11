#!/bin/bash
# harvest_pwrsys.sh
#
# Read the power system (PSC or MPEA) log files for the Endurance and Pioneer
# Coastal Surface Moorings and create parsed datasets available in JSON
# formatted files for further processing and review.
#
# C. Wingard 2015-04-17 -- Original code
# C. Wingard 2024-03-08 -- Updated to use the harvest_options.sh script to
#                          parse the command line inputs

# include the help function and parse the required and optional command line options
DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
source "$DIR/harvest_options.sh"

# check the processing flag for the correct power system type
case $SWITCH in
    "psc" | "mpea" | "syslog" )
        ;;
    * )
        echo "ERROR: Incorrect power system type, $FLAG, in the processing flag."
        echo "Please specify either psc, mpea or syslog (variant of the PSC) with"
        echo "the -f option."
        exit 1 # exit and indicate error
        ;;
esac

# Parse the file
if [ -e "$IN" ]; then
    cd /home/ooiuser/code/cgsn-parsers || exit
    python -m cgsn_parsers.parsers.parse_pwrsys -i "$IN" -o "$OUT" -s "$FLAG" || echo "ERROR: Failed to parse $IN"
fi
