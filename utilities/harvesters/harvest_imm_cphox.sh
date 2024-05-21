#!/bin/bash
# harvest_imm_cphox.sh
#
# Reads the raw SeaPhox imm data files (telemetered via the inductive modem) from the
# Global Surface Moorings and creates parsed datasets available in JSON
# formatted files for further processing and review.
#
# P. Whelan  2024-05-21 -- Original code

# include the help function and parse the required and optional command line options
DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
source "$DIR/harvest_options.sh"

# Parse the file
if [ -e "$IN_FILE" ]; then
    cd /home/ooiuser/code/cgsn-parsers || exit
    python -m cgsn_parsers.parsers.parse_imm_cphox -i "$IN_FILE" -o "$OUT_FILE"  || echo "ERROR: Failed to parse $IN_FILE"
fi

