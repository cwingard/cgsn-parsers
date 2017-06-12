#!/bin/bash -e
#
# Parse the various data files for a Coastal Surface Mooring.
#
# Wingard, C. 2015-04-17

# Parse the command line inputs
if [ $# -ne 3 ]; then
    echo "$0: required inputs are the platform and deployment name, the data file type and"
    echo "the data file type to process"
    echo "     example: $0 ce01issp D00006 PDB"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
TYPE=${3^^}

# setup the base directories and the python parser used for creating the JSON formatted file
RAW="/home/ooiuser/data/raw/$PLATFORM/$DEPLOY/extract"
PROC="/home/ooiuser/data/proc/$PLATFORM/$DEPLOY/$TYPE"
if [ ! -d $PROC ]; then
    # Make the output directory, if it doesn't exist
    /bin/mkdir -p $PROC
fi
PYTHON="/home/ooiuser/bin/conda/bin/python3"
# Process the profiler data, using the E files as the key.
case $TYPE in
    "ACS" )
        # OPTAA data files
        for file in $RAW/ucspp_*_ACS_ACS.txt; do
            out=`/bin/basename $file`
            if [ ! -f $PROC/${out%.txt}.json ]; then
                echo "Processing $file..."
                cd /home/ooiuser/code/cgsn-parsers
                $PYTHON -m cgsn_parsers.parsers.parse_ucspp_optaa -i $file -o $PROC/$out
            fi
        done ;;

    "PDB" | "PDD" )
        # CTDPF data files
        for file in $RAW/ucspp_*_$TYPE_CTD.txt; do
            out=`/bin/basename $file`
            if [ ! -f $PROC/${out%.txt}.json ]; then
                echo "Processing $file..."
                cd /home/ooiuser/code/cgsn-parsers
                $PYTHON -m cgsn_parsers.parsers.parse_ucspp_ctdpf -i $file -o $PROC/$out
            fi
        done

        # DOSTA data files
        for file in $RAW/ucspp_*_$TYPE_OPT.txt; do
            out=`/bin/basename $file`
            if [ ! -f $PROC/${out%.txt}.json ]; then
                echo "Processing $file..."
                cd /home/ooiuser/code/cgsn-parsers
                $PYTHON -m cgsn_parsers.parsers.parse_ucspp_dosta -i $file -o $PROC/$out
            fi
        done

        # FLORT data files
        for file in $RAW/ucspp_*_$TYPE_TRIP.txt; do
            out=`/bin/basename $file`
            if [ ! -f $PROC/${out%.txt}.json ]; then
                echo "Processing $file..."
                cd /home/ooiuser/code/cgsn-parsers
                $PYTHON -m cgsn_parsers.parsers.parse_ucspp_flort -i $file -o $PROC/$out
            fi
        done

        # PARAD data files
        for file in $RAW/ucspp_*_$TYPE_PAR.txt; do
            out=`/bin/basename $file`
            if [ ! -f $PROC/${out%.txt}.json ]; then
                echo "Processing $file..."
                cd /home/ooiuser/code/cgsn-parsers
                $PYTHON -m cgsn_parsers.parsers.parse_ucspp_parad -i $file -o $PROC/$out
            fi
        done

        # SPKIR data files
        for file in $RAW/ucspp_*_$TYPE_OCR.txt; do
            out=`/bin/basename $file`
            if [ ! -f $PROC/${out%.txt}.json ]; then
                echo "Processing $file..."
                cd /home/ooiuser/code/cgsn-parsers
                $PYTHON -m cgsn_parsers.parsers.parse_ucspp_spkir -i $file -o $PROC/$out
            fi
        done

        # VELPT data files
        for file in $RAW/ucspp_*_$TYPE_ADCP.txt; do
            out=`/bin/basename $file`
            if [ ! -f $PROC/${out%.txt}.json ]; then
                echo "Processing $file..."
                cd /home/ooiuser/code/cgsn-parsers
                $PYTHON -m cgsn_parsers.parsers.parse_ucspp_velpt -i $file -o $PROC/$out
            fi
        done ;;

    "SNA" )
        # NUTNR data files
        for file in $RAW/ucspp_*_SNA_SNA.txt; do
            out=`/bin/basename $file`
            if [ ! -f $PROC/${out%.txt}.json ]; then
                echo "Processing $file..."
                cd /home/ooiuser/code/cgsn-parsers
                $PYTHON -m cgsn_parsers.parsers.parse_ucspp_nutnr -i $file -o $PROC/$out
            fi
        done ;;

    "WC" )
        # HMR data files
        for file in $RAW/ucspp_*_WC_HMR.txt; do
            out=`/bin/basename $file`
            if [ ! -f $PROC/${out%.txt}.json ]; then
                echo "Processing $file..."
                cd /home/ooiuser/code/cgsn-parsers
                $PYTHON -m cgsn_parsers.parsers.parse_ucspp_wc_hmr -i $file -o $PROC/$out
            fi
        done

        # SBE data files
        for file in $RAW/ucspp_*_WC_SBE.txt; do
            out=`/bin/basename $file`
            if [ ! -f $PROC/${out%.txt}.json ]; then
                echo "Processing $file..."
                cd /home/ooiuser/code/cgsn-parsers
                $PYTHON -m cgsn_parsers.parsers.parse_ucspp_wc_sbe -i $file -o $PROC/$out
            fi
        done

        # WM data files
        for file in $RAW/ucspp_*_WC_WM.txt; do
            out=`/bin/basename $file`
            if [ ! -f $PROC/${out%.txt}.json ]; then
                echo "Processing $file..."
                cd /home/ooiuser/code/cgsn-parsers
                $PYTHON -m cgsn_parsers.parsers.parse_ucspp_wc_wm -i $file -o $PROC/$out
            fi
        done ;;

    * )
        echo "Unknown file type, please check the name again"
        exit 0 ;;
esac
