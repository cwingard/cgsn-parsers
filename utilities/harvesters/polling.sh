#!/bin/bash
# polling.sh
#
# Poll a directory for new or updated files and parse them using the specified
# command. This script is designed to be used with the harvesters to
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
#      inputs required for that command with the exception of the file path
#      and name.
#   2. The path to the directory to watch and the file pattern to monitor for
#      changes. The path and file pattern should be enclosed in double quotes
#      and the file pattern can include wildcards, although that is not true
#      for the path. For example, "/path/to/directory/*.txt" will monitor all
#      files with a .txt extension in /path/to/directory. Again, the path to
#      the directory CANNOT include wildcards, only the file name pattern.
#
# Example usage:
#   RAW_DATA="/home/ooiuser/data/raw/ce02shsm/D00017/cg_data"
#   HARVEST="/home/ooiuser/code/cgsn-parsers/utilities/harvesters"
#   INPUTS="ce02shsm D00017 buoy wavss"
#   cd $HARVEST
#   ./polling.sh "./harvest_wavss.sh $INPUTS" "$RAW_DATA/dcl12/wavss/*.log"
#
# The above example will monitor the wavss directory for new or updated files,
# passing them to the harvest_wavss.sh script
#
# One optional argument is available to reset the checksum files and force a
# re-parsing of the directory. This is useful when the parsing script has been
# updated and the directory needs to be re-parsed. To use this option, add
# a reset flag (-r) as the first argument. For example:
#
#   ./polling.sh -r "./harvest_wavss.sh $INPUTS" "$RAW_DATA/dcl12/wavss/*.log"
#
# An additional optional argument is available to skip creating the checksum
# files and force a re-parsing of the directory. This is useful when the same
# directory and file glob is being monitored by multiple scripts. To use this
# option, add a skip flag (-s) as the first argument. For example:
#
#   ./polling.sh -s "./harvest_syslog_gps.sh $INPUTS" "$RAW_DATA/syslog/*.log"
#
# A final option is available to monitor the same directory with different
# file patterns. This is useful when the same directory has multiple file
# patterns that need to be handled separately. To use this option, add a
# multiple flag (-m) with a unique value indicating the file pattern to
# monitor as the first argument. For example:
#
#   RAW_DATA="/home/ooiuser/data/raw/cp10cnsm/D0002/cg_data/dcl27/plims"
#   HARVEST="/home/ooiuser/code/cgsn-parsers/utilities/harvesters"
#   INPUTS="cp10cnsm D0002 nsif plims"
#   cd $HARVEST
#   ./polling.sh -m "hdr" "./harvest_ifcb.sh $INPUTS" "$RAW_DATA/*.hdr"
#   ./polling.sh -m "adc" "./harvest_ifcb_adc.sh $INPUTS" "$RAW_DATA/*.adc"
#
# Code inspired by: https://www.baeldung.com/linux/command-execute-file-dir-change
# with hints and suggestions from the GitHub CoPilot.
#
# C. Wingard 2024-03-08 -- Original code
# C. Wingard 2024-05-01 -- Added the skip option to allow for multiple scripts
#                          to monitor the same directory
# C. Wingard 2025-04-25 -- Added the multiple option to allow for different
#                          file patterns to be monitored in the same directory

help()
{
  # Display Help
  echo "Poll a directory for new or updated files and process them using the specified command."
  echo
  echo "Syntax: polling [OPTION] ""command_to_execute"" ""/path/to/directory/file_pattern"""
  echo "options:"
  echo "-h  Print this help message."
  echo "-m  Monitor the same directory with different file patterns."
  echo "-r  Reset the checksum files and force a re-parsing of the entire directory."
  echo "-s  Skip updating/creating the checksum files allowing for more than one"
  echo "                script to parse the same directory."
  echo
}

# First parse the optional command line inputs
RESET=0  # default to NOT resetting the checksum files
SKIP=0   # default to NOT skipping creating/updating the checksum files
MULTIPLE=0  # default to NOT monitoring multiple file patterns
while getopts "hm:rs" option; do
  # shellcheck disable=SC2214
  case "$option" in
    h ) # display help
      help
      exit;;
    m ) # multiple flag
      MULTIPLE=1
      MTYPE=${OPTARG,,}  # convert to lower case
      ;;
    r ) # reset flag
      RESET=1
      ;;
    s ) # skip flag
      SKIP=1
      ;;
    \?) # Invalid option
      echo "Error: Invalid option"
      help
      exit;;
  esac
done
shift $((OPTIND - 1))

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
# shellcheck disable=SC2086
if ! ls $PATH_GLOB 1> /dev/null 2>&1; then
    echo "ERROR: No files found matching the pattern: $PATH_GLOB"
    echo ""
    exit
fi

# set up the directory to watch and the checksum file to monitor for changes
DIR_TO_WATCH=$(dirname "$PATH_GLOB")
FILE_GLOB=$(basename "$PATH_GLOB")
echo "Monitoring $DIR_TO_WATCH for new or updated files matching $FILE_GLOB"

if [ $MULTIPLE -eq 1 ]; then
    DIRSHA=".directory_sha_$MTYPE"
    FILESHA=".file_stats_$MTYPE"
else
    DIRSHA=".directory_sha"
    FILESHA=".file_stats"
fi

# next, check if the checksum files exists (used to monitor for changes in the directory),
# if not, that means this is the first time we are processing this directory. parse all
# existing files, create the directory checksum and the file status to monitor for future
# changes, and exit
if [ $RESET -eq 1 ]; then
    # reset the checksum files and force a re-processing of the directory
    if [ -e "$DIR_TO_WATCH/$DIRSHA" ]; then
        echo "Resetting the checksum and file status records for $DIR_TO_WATCH prior to re-processing"
        rm -f "$DIR_TO_WATCH/$DIRSHA" "$DIR_TO_WATCH/$FILESHA"
    fi
fi
if [ ! -e "$DIR_TO_WATCH/$DIRSHA" ]; then
    echo "First processing run for $DIR_TO_WATCH, processing all files"
    # create a checksum of the directory contents and a listing of file stats to monitor for
    # future changes (directory as a whole and individual files based on size, creation and
    # modification times)
    if [ $SKIP -eq 1 ]; then
        echo "Skipping the creation of the checksum and file status records for $DIR_TO_WATCH"
    else
        find "$DIR_TO_WATCH" -name "$FILE_GLOB" -type f -exec stat -c "%s%W%Y%Z %n" {} + | sha1sum > "$DIR_TO_WATCH/$DIRSHA"  # directory as a whole
        find "$DIR_TO_WATCH" -name "$FILE_GLOB" -type f -exec stat -c "%s%W%Y%Z %n" {} + > "$DIR_TO_WATCH/$FILESHA"  # individual files in the directory
    fi
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
find "$DIR_TO_WATCH" -name "$FILE_GLOB" -type f -exec stat -c "%s%W%Y%Z %n" {} + | sha1sum --check --status "$DIR_TO_WATCH/$DIRSHA"
if [ $? -eq 1 ]; then
    echo "Contents of $DIR_TO_WATCH have changed, looking for new or modified files"
    TMPFILE=$(mktemp /tmp/polling-XXXXXXX)
    find "$DIR_TO_WATCH" -name "$FILE_GLOB" -type f -exec stat -c "%s%W%Y%Z %n" {} + > "$TMPFILE"
    # list any new or modified files based on the file stats
    UPDATED_FILES=$(sort "$TMPFILE" "$DIR_TO_WATCH/$FILESHA" | uniq -u | awk '{print $2}' | sort | uniq)
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
    if [ $SKIP -eq 1 ]; then
        echo "Skipping the creation of the checksum and file status records for $DIR_TO_WATCH"
    else
      find "$DIR_TO_WATCH" -name "$FILE_GLOB" -type f -exec stat -c "%s%W%Y%Z %n" {} + | sha1sum > "$DIR_TO_WATCH/$DIRSHA"  # directory as a whole
      find "$DIR_TO_WATCH" -name "$FILE_GLOB" -type f -exec stat -c "%s%W%Y%Z %n" {} + > "$DIR_TO_WATCH/$FILESHA"  # individual files in the directory
    fi
    rm "$TMPFILE"  # remove the temporary file
    exit  # exit with no error, updated files have been parsed
else
    echo "No new or modified files found in $DIR_TO_WATCH"
    echo ""
fi
