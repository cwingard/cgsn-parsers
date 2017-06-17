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
FTYPE=${3^^}

# setup the base directories and the python parser used for creating the JSON formatted file
RAW="/home/ooiuser/data/raw/$PLATFORM/$DEPLOY/extract"
PROC="/home/ooiuser/data/proc/$PLATFORM/$DEPLOY"
if [ ! -d $PROC ]; then
    # Make the output directory, if it doesn't exist
    /bin/mkdir -p $PROC
fi
PYTHON="/home/ooiuser/bin/conda/bin/python3"

case $FTYPE in
    "ACS" )
        # OPTAA data files
        ODIR="$PROC/optaa"
        if [ ! -d $ODIR ]; then
            mkdir -p $ODIR
        fi
        for file in $RAW/ucspp_*_ACS_ACS.txt; do
            out=`/bin/basename $file`
            if [ ! -f $ODIR/${out%.txt}.json ]; then
                echo "Processing $file..."
                cd /home/ooiuser/code/cgsn-parsers
                $PYTHON -m cgsn_parsers.parsers.parse_cspp_optaa -i $file -o $ODIR/${out%.txt}.json
            fi
        done ;;

    "PPB" | "PPD" )
        # CTDPF data files
        ODIR="$PROC/ctdpf"
        if [ ! -d $ODIR ]; then
            mkdir -p $ODIR
        fi
        for file in $RAW/ucspp_*_"$FTYPE"_CTD.txt; do
            out=`/bin/basename $file`
            if [ ! -f $ODIR/${out%.txt}.json ]; then
                echo "Processing $file..."
                cd /home/ooiuser/code/cgsn-parsers
                $PYTHON -m cgsn_parsers.parsers.parse_cspp_ctdpf -i $file -o $ODIR/${out%.txt}.json
            fi
        done

        # DOSTA data files
        ODIR="$PROC/dosta"
        if [ ! -d $ODIR ]; then
            mkdir -p $ODIR
        fi
        for file in $RAW/ucspp_*_"$FTYPE"_OPT.txt; do
            out=`/bin/basename $file`
            if [ ! -f $ODIR/${out%.txt}.json ]; then
                echo "Processing $file..."
                cd /home/ooiuser/code/cgsn-parsers
                $PYTHON -m cgsn_parsers.parsers.parse_cspp_dosta -i $file -o $ODIR/${out%.txt}.json
            fi
        done

        # FLORT data files
        ODIR="$PROC/flort"
        if [ ! -d $ODIR ]; then
            mkdir -p $ODIR
        fi
        for file in $RAW/ucspp_*_"$FTYPE"_TRIP.txt; do
            out=`/bin/basename $file`
            if [ ! -f $ODIR/${out%.txt}.json ]; then
                echo "Processing $file..."
                cd /home/ooiuser/code/cgsn-parsers
                $PYTHON -m cgsn_parsers.parsers.parse_cspp_flort -i $file -o $ODIR/${out%.txt}.json
            fi
        done

        # PARAD data files
        ODIR="$PROC/parad"
        if [ ! -d $ODIR ]; then
            mkdir -p $ODIR
        fi
        for file in $RAW/ucspp_*_"$FTYPE"_PARS.txt; do
            out=`/bin/basename $file`
            if [ ! -f $ODIR/${out%.txt}.json ]; then
                echo "Processing $file..."
                cd /home/ooiuser/code/cgsn-parsers
                $PYTHON -m cgsn_parsers.parsers.parse_cspp_parad -i $file -o $ODIR/${out%.txt}.json
            fi
        done

        # SPKIR data files
        ODIR="$PROC/spkir"
        if [ ! -d $ODIR ]; then
            mkdir -p $ODIR
        fi
        for file in $RAW/ucspp_*_"$FTYPE"_OCR.txt; do
            out=`/bin/basename $file`
            if [ ! -f $ODIR/${out%.txt}.json ]; then
                echo "Processing $file..."
                cd /home/ooiuser/code/cgsn-parsers
                $PYTHON -m cgsn_parsers.parsers.parse_cspp_spkir -i $file -o $ODIR/${out%.txt}.json
            fi
        done

        # VELPT data files
        ODIR="$PROC/velpt"
        if [ ! -d $ODIR ]; then
            mkdir -p $ODIR
        fi
        for file in $RAW/ucspp_*_"$FTYPE"_ADCP.txt; do
            out=`/bin/basename $file`
            if [ ! -f $ODIR/${out%.txt}.json ]; then
                echo "Processing $file..."
                cd /home/ooiuser/code/cgsn-parsers
                $PYTHON -m cgsn_parsers.parsers.parse_cspp_velpt -i $file -o $ODIR/${out%.txt}.json
            fi
        done

        ;;

    "SNA" )
        # NUTNR data files
        ODIR="$PROC/nutnr"
        if [ ! -d $ODIR ]; then
            mkdir -p $ODIR
        fi
        for file in $RAW/ucspp_*_SNA_SNA.txt; do
            out=`/bin/basename $file`
            if [ ! -f $ODIR/${out%.txt}.json ]; then
                echo "Processing $file..."
                cd /home/ooiuser/code/cgsn-parsers
                $PYTHON -m cgsn_parsers.parsers.parse_cspp_nutnr -i $file -o $ODIR/${out%.txt}.json
            fi
        done ;;

    "WC" )
        # HMR data files
        ODIR="$PROC/winch"
        if [ ! -d $ODIR ]; then
            mkdir -p $ODIR
        fi
        for file in $RAW/ucspp_*_WC_HMR.txt; do
            out=`/bin/basename $file`
            if [ ! -f $ODIR/${out%.txt}.json ]; then
                echo "Processing $file..."
                cd /home/ooiuser/code/cgsn-parsers
                $PYTHON -m cgsn_parsers.parsers.parse_cspp_wc_hmr -i $file -o $ODIR/${out%.txt}.json
            fi
        done

        # SBE data files
        for file in $RAW/ucspp_*_WC_SBE.txt; do
            out=`/bin/basename $file`
            if [ ! -f $ODIR/${out%.txt}.json ]; then
                echo "Processing $file..."
                cd /home/ooiuser/code/cgsn-parsers
                $PYTHON -m cgsn_parsers.parsers.parse_cspp_wc_sbe -i $file -o $ODIR/${out%.txt}.json
            fi
        done

        # WM data files
        for file in $RAW/ucspp_*_WC_WM.txt; do
            out=`/bin/basename $file`
            if [ ! -f $ODIR/${out%.txt}.json ]; then
                echo "Processing $file..."
                cd /home/ooiuser/code/cgsn-parsers
                $PYTHON -m cgsn_parsers.parsers.parse_cspp_wc_wm -i $file -o $ODIR/${out%.txt}.json
            fi
        done ;;

    * )
        echo "Unknown file type, please check the name again"
        exit 0 ;;
esac
