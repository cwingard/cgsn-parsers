#!/usr/bin/env bash
#
# Read the STC data and the raw, telemetered MMP data files for the Coastal Profiler Moorings
# and create parsed data sets available in TXT and JSON files for further processing and
# review. Utilizes the mmp_unpack utility created by Jeff O'Brien of WHOI. Traps
# files that fail to process using a timeout control. Files that fail to process
# are tagged with a .failed on the end of the file name to help indicate a problem.
#
# C. Wingard 2017-02-23 -- Original Code
# C. Wingard 2017-03-01 -- Updated to use the new polling script

# Parse the command line inputs
if [ $# -ne 2 ]; then
    echo "$0: required inputs are the platform and deployment name"
    echo "     example: $0 ce09ospm D00019"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}

# set the directory for the raw data and the harvesting scripts
RAW="/home/ooiuser/data/raw/$PLATFORM/$DEPLOY/cg_data"
HARVEST="/home/ooiuser/code/cgsn-parsers/utilities/harvesters"
cd "$HARVEST" || exit

# load the ooi python environment
. $(dirname $CONDA_EXE)/../etc/profile.d/conda.sh
conda activate ooi

#### Buoy Instruments ####
assembly="buoy"  # surface buoy with CPM1 (and auxiliary instruments)
./polling.sh "$HARVEST/harvest_superv_stc.sh $PLATFORM $DEPLOY $assembly superv" "$RAW/syslog/*.syslog.log"
./polling.sh "$HARVEST/harvest_syslog_gps.sh $PLATFORM $DEPLOY $assembly gps" "$RAW/syslog/*.syslog.log"
./polling.sh "$HARVEST/harvest_syslog_irid.sh $PLATFORM $DEPLOY $assembly irid" "$RAW/syslog/*.syslog.log"
./polling.sh "$HARVEST/harvest_mopak.sh $PLATFORM $DEPLOY $assembly mopak" "$RAW/3dmgx3/*.3dmgx3.log"

# And now process the MMP data, first setting the MMP input and output directories
RAW="$RAW/imm/mmp"
PARSED="/home/ooiuser/data/parsed/$PLATFORM/$DEPLOY/imm/mmp"
if [ ! -d $PARSED ]; then
    # Make the output directory, if it doesn't exist
    /bin/mkdir -p $PARSED
fi

# set up the unpacker and a limit of 5 seconds for processing (takes less than a second normally)
UNPACK="/usr/bin/timeout 5 /home/ooiuser/bin/cg_util/mmp_unpack"

# Process the profiler data, using the E files as the key.
for file in "$RAW"/E*.DAT; do
    # unpack the file, if it hasn't already been processed
    out=$(basename $file)
    eng="$PARSED/${out%.DAT}.TXT"
    if [ ! -e $eng ] || [ ! -e $eng.failed ]; then
        echo "Processing $file..."
        # check to see if we already have created TIMETAGS2.TXT, don't want to overwrite
        if [ -f $PARSED/TIMETAGS2.TXT ]; then
            /bin/cp $PARSED/TIMETAGS2.TXT timetags
        fi

        # generate the TIMETAGS2.TXT file
        echo -e "\tGenerating TIMETAGS2"
        if $UNPACK $PARSED $file -t; then
            # Extract successful, append results to the TIMETAGS2 file
            if [ -f timetags ]; then
                # If we already have an existing TIMETAGS2 file, append results from the newly created one
                /usr/bin/tail -1 $PARSED/TIMETAGS2.TXT >> timetags
                /bin/mv timetags $PARSED/TIMETAGS2.TXT
            fi
            /bin/cp -f $PARSED/TIMETAGS2.TXT $RAW/TIMETAGS2.TXT
        else
            # Extract failed, create empty file indicating failure and skip to next file
            /bin/echo -e "\tCorrupted file, skipping file"
            /bin/touch $PARSED/${out%.DAT}.TXT.failed
            if [ -e timetags ]; then
                # replace TIMETAGS2
                /bin/mv timetags $PARSED/TIMETAGS2.TXT
            fi
            continue
        fi
        # now extract all of the data from the E file
        /bin/echo -e "\tExtracting Engineering and ECO Triplet"
        $UNPACK $PARSED $file
    fi

    # check to see if we have a corresponding C file, unpack if not already done
    ctd=$PARSED/${out%.DAT}.TXT
    ctd=${ctd/E/C}
    if [ -f ${file/E/C} ] && [ ! -f $ctd ]; then
        /bin/echo -e "\tExtracting CTD and Oxygen"
        if ! $UNPACK $PARSED ${file/E/C}; then
            # extract failed
            /bin/mv $ctd $ctd.failed
        fi
    fi

    # check to see if we have a corresponding A file, unpack if not already done
    vel=$PARSED/${out%.DAT}.TXT
    vel=${vel/E/A}
    A=${file/E/A}; A=${A%.DAT}.DEC
    if [ -f $A ] && [ ! -f $vel ]; then
        /bin/echo -e "\tExtracting Velocity"
        if ! $UNPACK $PARSED $A; then
            # extract failed
            /bin/mv $vel $vel.failed
        fi
    fi

    # now we can create our JSON formatted file, if we haven't already
    profile=${eng/E/P}
    profile=${profile%.TXT}.json
    if [ -f $eng ] && [ -f $ctd ] && [ -f $vel ] && [ ! -f $profile ]; then
        /bin/echo -e "Creating Profile: $profile\n"
        cd /home/ooiuser/code/cgsn-parsers || exit
        python -m cgsn_parsers.parsers.parse_mmp_coastal -i $eng -o $profile || echo "ERROR: Failed to create $profile"
    fi
done

# clean up
/bin/rm -f timetags
