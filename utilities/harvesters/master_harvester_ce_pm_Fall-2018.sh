#!/usr/bin/env bash
#
# Read the STC data and the raw, telemetered MMP data files for the Coastal Profiler Moorings
# and create parsed data sets available in TXT and JSON files for further processing and
# review. Utilizes the mmp_unpack utility created by Jeff O'Brien of WHOI. Traps
# files that fail to process using a timeout control. Files that fail to process
# are tagged with a .failed on the end of the file name to help indicate a problem.
#
# Wingard, C. 2017-02-23

# Parse the command line inputs
if [ $# -ne 3 ]; then
    echo "$0: required inputs are the platform and deployment name, and"
    echo "the time flag for processing today's file (0) or N days prior"
    echo "     example: $0 ce02shsm D00001 0"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
TIME="-$3 day"
FNAME=`/bin/date -u +%Y%m%d --date="$TIME"`

# First we are going to process any syslog (for iridium, gps and supervisor data) or mopak data sent by the mooring
RAW="/home/ooiuser/data/raw"
HARVEST="/home/ooiuser/code/cgsn-parsers/utilities/harvesters"
source activate ooi

$HARVEST/harvest_superv_stc.sh $PLATFORM $DEPLOY $FNAME.syslog.log
$HARVEST/harvest_syslog_gps.sh $PLATFORM $DEPLOY $FNAME.syslog.log
$HARVEST/harvest_syslog_irid.sh $PLATFORM $DEPLOY $FNAME.syslog.log
for mopak in $RAW/$PLATFORM/$DEPLOY/3dmgx3/$FNAME*.3dmgx3.log; do
    if [ -e $mopak ]; then
        SIZE=`du -k "$mopak" | cut -f1`
        if [ $SIZE -gt 0 ]; then
            $HARVEST/harvest_3dmgx3.sh $PLATFORM $DEPLOY $mopak
        fi
    fi
done

# If there is any ADCP data sent via the inductive modem, process it now
if [ -d $RAW/$PLATFORM/$DEPLOY/imm/adcp* ]; then
    for adcp in $RAW/$PLATFORM/$DEPLOY/imm/adcp*/adcp*_$FNAME*.DAT; do
        if [ -e $adcp ]; then
            SIZE=`du -k "$adcp" | cut -f1`
            if [ $SIZE -gt 0 ]; then
                $HARVEST/harvest_imm_adcp.sh $PLATFORM $DEPLOY $adcp
            fi
        fi
    done
fi

# And now process the MMP data, first setting the MMP input and output directories
RAW="/home/ooiuser/data/raw/$PLATFORM/$DEPLOY/imm/mmp"
PROC="/home/ooiuser/data/proc/$PLATFORM/$DEPLOY/imm/mmp"
if [ ! -d $PROC ]; then
    # Make the output directory, if it doesn't exist
    /bin/mkdir -p $PROC
fi

# set the unpacker and a limit of 5 seconds for processing (takes less than a second normally)
UNPACK="/usr/bin/timeout 5 /home/ooiuser/bin/cg_util/mmp_unpack"

# setup the python parser used for creating the JSON formatted file

# Process the profiler data, using the E files as the key.
for file in $RAW/E*.DAT; do
    # unpack the file, if it hasn't already been processed
    out=`basename $file`
    if [ ! -f $PROC/${out%.DAT}.TXT* ]; then
        echo "Processing $file..."

        # check to see if we already have created TIMETAGS2.TXT, don't want to overwrite
        if [ -f $PROC/TIMETAGS2.TXT ]; then
            /bin/cp $PROC/TIMETAGS2.TXT timetags
        fi

        # generate the TIMETAGS2.TXT file
        echo -e "\tGenerating TIMETAGS2"
        $UNPACK $PROC $file -t

        # check to see if we were successful
        if [ $? -eq 0 ]; then
            # Success!
            if [ -f timetags ]; then
                # If we already have an existing TIMETAGS2 file, append results
                /usr/bin/tail -1 $PROC/TIMETAGS2.TXT >> timetags
                /bin/mv timetags $PROC/TIMETAGS2.TXT
            fi
        else
            # Extract failed, create empty file indicating failure and skip to next file
            /bin/echo -e "\tCorrupted file, skipping file"
            /bin/touch $PROC/${out%.DAT}.TXT.failed
            if [ -f timetags ]; then
                # replace TIMETAGS2
                /bin/mv timetags $PROC/TIMETAGS2.TXT
            fi
            continue
        fi

        # now extract the data from the E, C, and A files
        ### Engineering and ECO Triplet data
        /bin/echo -e "\tExtracting Engineering and ECO Triplet"
        $UNPACK $PROC $file
        declare -i count=1

        ### CTD and Oxygen data
        if [ -f ${file/E/C} ]; then
            /bin/echo -e "\tExtracting CTD and Oxygen"
            ctd=$PROC/${out%.DAT}.TXT
            ctd=${ctd/E/C}
            $UNPACK $PROC ${file/E/C}
            if [ $? -ne 0 ]; then
                # extract failed
                /bin/mv $ctd $ctd.failed
            else
                count=$count+1
            fi
        fi

        ### Velocity data
        A=${file/E/A}; A=${A%.DAT}.DEC
        if [ -f $A ]; then
            /bin/echo -e "\tExtracting Velocity"
            vel=$PROC/${out%.DAT}.TXT
            vel=${vel/E/A}
            $UNPACK $PROC $A
            if [ $? -ne 0 ]; then
                # extract failed
                /bin/mv $vel $vel.failed
            else
                count=$count+1
            fi
        fi

        ### And now we can create our JSON formatted file
        if [ $count -eq 3 ]; then
            infile=$PROC/${out%.DAT}.TXT
            outfile=${infile/E/P}
            outfile=${outfile%.TXT}.json
            cd /home/ooiuser/code/cgsn-parsers
            python -m cgsn_parsers.parsers.parse_mmp_coastal -i $infile -o $outfile
        fi
    fi
done

# clean up
/bin/rm -f timetags
