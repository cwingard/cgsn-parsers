#!/bin/bash
# polling.sh
#
# Poll a directory for new or updated files and parse them using the
# specified command. This script is designed to be used with the harvesters to
# monitor a directory for new or updated files and parse them as they are added
# to the directory. Note, this script can also be used with the processing
# scripts available in cgsn_processing to monitor a directory for new or
# updated files and process them as they are added to the directory.
#
# The use of inotify is not possible in the OOI environment, as our data
# is stored on network file systems. This script is a simple polling script
# that checks for new or updated files in the directory based on a schedule set
# via the crontab.
#
# The script takes two arguments:
#   1. The command to execute when new or updated files are detected. The
#      command should be enclosed in double quotes and include all other
#      required inputs.
#   2. The path to the directory to watch and the file pattern to monitor for
#      changes. The path and file pattern should be enclosed in double quotes
#      and the file pattern can include wildcards, although that is not true
#      for the path.
#      For example, "/path/to/directory/*.txt" will monitor all files with a
#      .txt extension in /path/to/directory. Again, the path to the directory
#      CANNOT include wildcards, only the file name pattern.
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
#   ./polling.sh -r "./harvest_wavss.sh $INPUTS" "$RAW_DATA/dcl12/wavss/*.log"
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
COMMAND=${1}
PATH_GLOB=${2}

# check if the directory/file pattern matches any files (can happen if the directory is empty,
# nonexistent or the pattern is in some way incorrect)
if ! ls $PATH_GLOB 1> /dev/null 2>&1; then
    echo "ERROR: No files found matching the pattern: $PATH_GLOB"
    echo ""
    exit
fi

# set up the directory to watch and the checksum file to monitor for changes
DIR_TO_WATCH=$(dirname "$PATH_GLOB")
FILE_GLOB=$(basename "$PATH_GLOB")
echo "Monitoring $DIR_TO_WATCH for new or updated files matching $FILE_GLOB"

# next, check if the checksum files exists (used to monitor for changes in the directory),
# if not, that means this is the first time we are processing this directory. parse all
# existing files, create the directory checksum and the file status to monitor for future
# changes, and exit
if [ $RESET -eq 1 ]; then
    # reset the checksum files and force a re-processing of the directory
    if [ -e "$DIR_TO_WATCH/.directory_sha" ]; then
        echo "Resetting the checksum and file status records for $DIR_TO_WATCH prior to re-processing"
        rm -f "$DIR_TO_WATCH/.directory_sha" "$DIR_TO_WATCH/.file_stats"
    fi
fi
if [ ! -e "$DIR_TO_WATCH/.directory_sha" ]; then
    echo "First processing run for $DIR_TO_WATCH, processing all files"
    # create a checksum of the directory contents and a listing of file stats to monitor for
    # future changes (directory as a whole and individual files based on size, creation and
    # modification times)
    find $DIR_TO_WATCH -name $FILE_GLOB -type f -exec stat -c "%s%W%Y%Z %n" {} + | sha1sum > "$DIR_TO_WATCH/.directory_sha"  # directory as a whole
    find $DIR_TO_WATCH -name $FILE_GLOB -type f -exec stat -c "%s%W%Y%Z %n" {} + > "$DIR_TO_WATCH/.file_stats"  # individual files in the directory
    # process all the files in the directory (using parallel processing to parse up to 7 files at a time)
    for file in $PATH_GLOB; do
        (
            echo "Processing $file"
            eval '$COMMAND $file'
        ) &
        if (( $(jobs | wc -l) >= 7 )); then
            # wait until there is a free slot for a new job
            wait -n
        fi
    done
    echo "First processing run complete for $DIR_TO_WATCH"
    echo ""
    exit  # exit with no error, the directory has been parsed for the first time
fi

# The directory exists, it is not empty and the checksum file exists, checking for new or updated files
find $DIR_TO_WATCH -name $FILE_GLOB -type f -exec stat -c "%s%W%Y%Z %n" {} + | sha1sum --check --status "$DIR_TO_WATCH/.directory_sha"
if [ $? -eq 1 ]; then
    echo "Contents of $DIR_TO_WATCH have changed, looking for new or modified files"
    TMPFILE=$(mktemp /tmp/processing-XXXXXXX)
    find $DIR_TO_WATCH -name $FILE_GLOB -type f -exec stat -c "%s%W%Y%Z %n" {} + > $TMPFILE
    # list any new or modified files based on the file stats
    UPDATED_FILES=$(sort $TMPFILE "$DIR_TO_WATCH/.file_stats" | uniq -u | awk '{print $2}' | sort | uniq)
    if [ -n "$UPDATED_FILES" ]; then
        # Parse the files (using parallel processing to parse up to 7 files at a time)
        for file in $UPDATED_FILES; do
            (
                echo "Processing $file"
                eval '$COMMAND $file'
            ) &
            if (( $(jobs | wc -l) >= 7 )); then
                # wait until there is a free slot for a new job
                wait -n
            fi
        done
        echo "Updated file processing complete for $DIR_TO_WATCH"
        echo ""
    fi
    # update the directory and file list checksums and exit
    find $DIR_TO_WATCH -name $FILE_GLOB -type f -exec stat -c "%s%W%Y%Z %n" {} + | sha1sum > "$DIR_TO_WATCH/.directory_sha"  # directory as a whole
    find $DIR_TO_WATCH -name $FILE_GLOB -type f -exec stat -c "%s%W%Y%Z %n" {} + > "$DIR_TO_WATCH/.file_stats"  # individual files in the directory
    rm $TMPFILE  # remove the temporary file
    exit  # exit with no error, updated files have been parsed
else
    echo "No new or modified files found in $DIR_TO_WATCH"
    echo ""
fi
