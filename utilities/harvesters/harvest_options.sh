#!/bin/bash
# harvest_options.sh
#
# This script is used to parse the command line inputs for the harvesters and
# provide a help function to display the required and optional inputs for the
# harvester scripts.
#
# C. Wingard  2024-02-02 Original code

# create a function to print the help documentation
function help ()
{
  echo "$0: required inputs are the mooring, deployment, platform and instrument names, in"
  echo "that order, followed by the name of the file to parse. An optional flag can be set"
  echo "through the use of the -f option as defined below:"
  echo ""
  echo "Syntax: $0 [-h|f] <mooring> <deployment> <platform> <instrument> <file>"
  echo ""
  echo "Options:"
  echo "h    Print this help message and exit."
  echo "f    Value of the processing flag, if used. Value parser specific (optional)."
  echo ""
  echo "The input names set the directory structure for where the parsed data files are"
  echo "stored. The file name is the name of the file to parse (either relative or full"
  echo "path information is required). Note, the instrument name can include relative path"
  echo "information, if needed. For example, the instrument name could be specified as"
  echo "'superv/dcl17' to indicate the parsed would be located in the 'superv/dcl17'"
  echo "directory."
  echo "Example: $0 ce02shsm D00001 cpm1 2018-01-01.cpm.log"
}

# Parse the optional command line inputs
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

# Parse the required command line inputs
echo $#
if [ $# -ne 5 ]; then
  echo "Error: Incorrect number of inputs. Please specify the mooring, deployment, platform,"
  echo "and instrument names and the file to parse, in that order."
  echo " "
  help
fi
MOORING=${1,,}
DEPLOY=${2^^}
PLATFORM=${3,,}
INSTRMT=${4,,}
FILE=${5}
FNAME=$(basename "$FILE")
