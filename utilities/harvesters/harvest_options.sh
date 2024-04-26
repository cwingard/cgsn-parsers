#!/bin/bash
# harvest_options.sh
#
# This script is used to parse the command line inputs for the harvesters and
# provide a help function to display the required and optional inputs for the
# harvester scripts.
#
# C. Wingard 2024-02-02 -- Original code

# create a function to print the help documentation
function help ()
{
  echo "$0: required inputs are the mooring, deployment, subassembly and"
  echo "instrument names, in that order, followed by the name of the file to"
  echo "parse. An optional flag can be set through the use of the -f option"
  echo "as defined below:"
  echo ""
  echo "Syntax: $0 [-h|f] mooring deployment subassembly instrument file"
  echo ""
  echo "Options:"
  echo "h    Print this help message and exit."
  echo "f    Value of the processing flag, if used. Value is parser specific,"
  echo "     can be either a string, integer or float (optional)."
  echo ""
  echo "The inputs set the directory structure for where the parsed data"
  echo "files are stored. The file name is the name of the file to parse"
  echo "(either relative or full path information is required). Note, the"
  echo "instrument name can include relative path information, if needed. For"
  echo "example, the instrument name could be specified as 'superv/dcl17' to"
  echo "indicate the parsed data would be located in the 'superv/dcl17'"
  echo "directory."
  echo ""
  echo "Example: $0 ce02shsm D00017 buoy superv/cpm1 20240202.superv.log"
}

# First parse the optional command line inputs
while getopts "hf:" option; do
  case $option in
    h ) # display Help
      help
      exit;;
    f ) # Processing flag
      FLAG=${OPTARG,,}
      shift $((OPTIND - 1))
      ;;
    * ) # Invalid option
      echo "Error: Invalid option"
      exit 1;;
  esac
done

# Then parse the required command line inputs and check the number of inputs
if [ $# -ne 5 ]; then
  echo "Error: Incorrect number of inputs. Please specify the mooring, deployment,"
  echo "subassembly, and instrument names and the file to parse, in that order."
  echo ""
  help
fi
MOORING=${1,,}
DEPLOY=${2^^}
ASSMBLY=${3,,}
INSTRMT=${4,,}
IN_FILE=${5}
FNAME=$(basename "$IN_FILE")

# test if the input file exists and is not empty
if [ ! -s "$IN_FILE" ]; then
  echo "ERROR: The input file $IN_FILE does not exist or is empty."
  exit 0
fi

# Set the parsed output data directory
PARSED="/home/ooiuser/data/parsed"
OUT_DIR="$PARSED/$MOORING/$DEPLOY/$ASSMBLY/$INSTRMT"
OUT_FILE="$OUT_DIR/${FNAME%.log}.json"
if [ ! -d "$OUT_DIR" ]; then
    mkdir -p "$OUT_DIR"
fi
