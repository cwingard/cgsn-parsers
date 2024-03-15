#!/bin/bash
# polling.sh
#
# Poll a directory for new or updated files and process them using the
# specified command. This script is designed to be used with the harvesters to
# monitor a directory for new or updated files and parse them as they are added
# to the directory.
#
# Note, the use of inotify is not possible in the OOI environment, as our data
# is stored on a network file system. This script is a simple polling script
# that checks for new or updated files in the directory based on a schedule set
# via the crontab (usually every 30 minutes).
#
# The script takes two arguments:
#   1. The command to execute when new or updated files are detected. The
#      command should be in quotes and include all other required inputs.
#   2. The path to the directory to watch and the file pattern to monitor for
#      changes. The file pattern should be in quotes and can include wildcards.
#      For example, "/path/to/directory/*.txt" will monitor all files with a
#      .txt extension in /path/to/directory. Note, the path to the directory
#      CANNOT include wildcards, only the file name itself.
#
# Example usage:
#   RAW_DATA="/home/ooiuser/data/raw/ce02shsm/D00017/cg_data"
#   HARVEST="/home/ooiuser/code/cgsn-parsers/utilities/harvesters"
#   INPUTS="ce02shsm D00017 buoy wavss"
#   cd $HARVEST
#   ./polling.sh "./harvest_wavss.sh $INPUTS" "$RAW_DATA/dcl12/wavss/*.log"
#
# The above example will monitor the wavss directory for new or updated files, running
# them through the harvest_wavss.sh script
#
# One optional argument is available to reset the checksum files and force a
# re-parsing of the directory. This is useful when the parsing script has been
# updated and the directory needs to be re-parsed. To use this option, add
# a reset flag (-r) as the first argument. For example:
#
#   ./polling.sh -r ./harvest_wavss.sh $INPUTS" "$RAW_DATA/dcl12/wavss/*.log"
#
# Code inspired by: https://www.baeldung.com/linux/command-execute-file-dir-change
# with hints and suggestions from the GitHub CoPilot.
#
# C. Wingard 2024-03-08 -- Original code

help()
{
   # Display Help
   echo "Poll a directory for new or updated files and process them using the"
   echo "specified command."
   echo
   echo "Syntax: polling [-h|r] <command to execute> <path to directory and file pattern>"
   echo "options:"
   echo "h     Print this help."
   echo "r     Reset the checksum files and force a re-parsing of the directory."
   echo
}

# First parse the optional command line inputs
RESET=0  # default to not reset the checksum files
while getopts "hr" option; do
  case $option in
    h ) # display help
      help
      exit;;
    r ) # reset flag
      RESET=1
      shift $((OPTIND - 1))
      ;;
    \?) # Invalid option
      echo "Error: Invalid option"
      exit;;
  esac
done

# Parse the command line inputs
if [ "$#" -ne 2 ]; then
    echo "ERROR: Incorrect number of arguments"
    echo "Usage: $0 <command to execute> <path to directory and file pattern>"
    exit 1
fi
# shellcheck disable=SC2034
COMMAND=${2}
PATH_GLOB=${3}

# set up the directory to watch and the checksum file to monitor for changes
DIR_TO_WATCH=$(dirname "$PATH_GLOB")
if [ ! -d "$DIR_TO_WATCH" ]; then
    # first check if the directory exists
    echo "ERROR: Directory to watch does not exist: $DIR_TO_WATCH"
    exit  # exit with no error so we don't stop the larger batch process
fi

# now check if there are any files in the directory
echo "Watching directory: $DIR_TO_WATCH"
if [ -z "$(ls -A "$DIR_TO_WATCH")" ]; then
    echo "Directory $DIR_TO_WATCH is empty, no files to process at this time"
    exit  # exit with no error, the directory exists but is empty (can happen if data telemetry is just starting up)
fi

# next, check if the checksum files exists (used to monitor for changes in the directory),
# if not, that means this is the first time we are parsing this directory. parse all
# existing files, create the checksum files to monitor for future changes, and exit
if [ $RESET -eq 1 ]; then
    # reset the checksum files and force a re-parsing of the directory
    echo "Resetting the checksum files for $DIR_TO_WATCH"
    rm -f "$DIR_TO_WATCH/checksum_dir.sha" "$DIR_TO_WATCH/checksum_files.sha"
fi
if [ ! -e "$DIR_TO_WATCH/checksum_dir.sha" ]; then
    # process all the files in the directory
    echo "First parsing run for $DIR_TO_WATCH, parsing all files..."
    # Parse the files (using parallel processing to parse up to 7 files at a time)
    for file in $PATH_GLOB; do
        (
            echo "Parsing $file"
            eval '$COMMAND $file'
        ) &
        if (( $(jobs | wc -l) >= 7 )); then
            # wait until there is a free slot for a new job
            wait -n
        fi
    done
    # create the checksum files to monitor for changes (directory as a whole and individual files)
    echo "Creating the checksum files for $DIR_TO_WATCH"
    # shellcheck disable=SC2012
    ls -l --full-time $PATH_GLOB | sha1sum > "$DIR_TO_WATCH/checksum_dir.sha"  # directory as a whole
    sha1sum $PATH_GLOB > "$DIR_TO_WATCH/checksum_files.sha"  # individual files in the directory
    exit  # exit with no error, the directory has been parsed for the first time
fi

# The directory exists, it is not empty and the checksum file exists, checking for new or updated files
# shellcheck disable=SC2012
ls -l --full-time $PATH_GLOB | sha1sum --check --status "$DIR_TO_WATCH/checksum_dir.sha"
if [ $? -eq 1 ]; then
    echo "Contents of $DIR_TO_WATCH have changed, looking for modified files..."
    TMPFILE=$(mktemp /tmp/parsing-XXXXX.sha)
    sha1sum $PATH_GLOB > $TMPFILE
    # list any new or modified files based on the checksums
    UPDATED_FILES=$(sort $TMPFILE "$DIR_TO_WATCH/checksum_files.sha" | uniq -u | awk '{print $2}' | sort | uniq)
    if [ -n "$UPDATED_FILES" ]; then
        # Parse the files (using parallel processing to parse up to 7 files at a time)
        for file in $UPDATED_FILES; do
            (
                echo "Parsing $file"
                eval '$COMMAND $file'
            ) &
            if (( $(jobs | wc -l) >= 7 )); then
                # wait until there is a free slot for a new job
                wait -n
            fi
        done
    fi
    # update the directory and file list checksums and exit
    # shellcheck disable=SC2012
    ls -l --full-time $PATH_GLOB | sha1sum > "$DIR_TO_WATCH/checksum_dir.sha"  # directory as a whole
    sha1sum $PATH_GLOB > "$DIR_TO_WATCH/checksum_files.sha"  # individual files in the directory
    rm $TMPFILE  # clean up the temporary file
    exit  # exit with no error, updated files have been parsed
fi
