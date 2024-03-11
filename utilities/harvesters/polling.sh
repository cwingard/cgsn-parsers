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
#   1. The path to the directory to watch and the file pattern to monitor for
#      changes. The file pattern should be in quotes and can include wildcards.
#      For example, "/path/to/directory/*.txt" will monitor all files with a
#      .txt extension in /path/to/directory.
#   2. The command to execute when new or updated files are detected. The
#      command should be in quotes and include the full path to the script or
#      program to execute including all needed inputs.
#
# Example usage:
#   RAW_DATA="/home/ooiuser/data/raw/ce02shsm/D00017/cg_data"
#   HARVEST="/home/ooiuser/code/cgsn-parsers/utilities/harvesters"
#   INPUTS="ce02shsm D00017 buoy wavss"
#   ./polling.sh "$RAW_DATA/dcl12/wavss/*.log" "$HARVEST/harvest_wavss.sh $INPUTS"
#
# The above example will monitor the /home/ooiuser/data/raw/ce02shsm/D00017/cg_data/dcl12/wavss
# directory for new or updated .log files and execute the harvest_wavss.sh script
#
# Code inspired by: https://www.baeldung.com/linux/command-execute-file-dir-change
# C. Wingard 2024-03-08 -- Original code

# Parse the command line inputs
if [ "$#" -ne 2 ]; then
    echo "ERROR: Incorrect number of arguments"
    echo "Usage: $0 <path to directory and file pattern> <command to execute>"
    exit 1
fi
PATH_GLOB=${1}
COMMAND=${2}

# set up the directory to watch and the checksum file to monitor for changes
DIR_TO_WATCH=$(dirname "$PATH_GLOB")
if [ ! -d "$DIR_TO_WATCH" ]; then
    # first check if the directory exists
    echo "ERROR: Directory to watch does not exist: $DIR_TO_WATCH"
    exit 1  # exit with an error, the directory does not exist
fi

# now check if there are any files in the directory
echo "Watching directory: $DIR_TO_WATCH"
if [ -z "$(ls -A "$DIR_TO_WATCH")" ]; then
    echo "Directory $DIR_TO_WATCH is empty, no files to process at this time"
    exit 0  # exit with no error, the directory exists but is empty (can happen if the directory is new)
fi

# next, check if the checksum file exists (used to monitor for changes in the directory),
# if not, that means this is the first time we are parsing this directory. parse all
# existing files, create the checksum file to monitor for future changes, and exit
if [ ! -e "$DIR_TO_WATCH/checksum.sha256" ]; then
    # process all the files in the directory
    echo "First parsing run for $DIR_TO_WATCH, parsing all files..."
    for file in $PATH_GLOB; do
        echo "Parsing $file"
        $COMMAND "$file"
    done
    # create the checksum file
    echo "Creating the checksum file for $DIR_TO_WATCH"
    # shellcheck disable=SC2012
    ls -l --full-time $PATH_GLOB | sha256sum > "$DIR_TO_WATCH/checksum.sha256"
    exit 0  # exit with no error, the directory has been parsed for the first time
fi

# The directory exists, it is not empty and the checksum file exists, checking for new or updated files
# shellcheck disable=SC2012
ls -l --full-time $PATH_GLOB | sha256sum --check --status "$DIR_TO_WATCH/checksum.sha256"
if [ $? -eq 1 ]; then
    echo "Updated files detected in $DIR_TO_WATCH, parsing the updated files..."
    # list files created or modified in the last 30 + 5 minutes (allowing for a 5 minute delay in the file system)
    UPDATED_FILES=$(find $PATH_GLOB -type f -mmin -35)
    for file in $UPDATED_FILES; do
        echo "Parsing $file"
        $COMMAND "$file"
    done
    # update the checksum file
    # shellcheck disable=SC2012
    ls -l --full-time $PATH_GLOB | sha256sum > "$DIR_TO_WATCH/checksum.sha256"
    exit 0  # exit with no error, updated files have been parsed
fi
