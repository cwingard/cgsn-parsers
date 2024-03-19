#!/bin/bash -e
#
# Parse the various data files for uncabled Coastal Surface Piercing Profiler (uCSPP).
#
# C. Wingard 2015-04-17 -- Original Code
# C. Wingard 2024-03-12 -- Updated for minor changes in the structure of the data directories

# Parse the command line inputs
if [ $# -ne 3 ]; then
    echo "$0: required inputs are the platform and deployment name, the data file type and"
    echo "the data file type to process"
    echo "     example: $0 ce01issp D00006 PPB"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
FTYPE=${3^^}

# setup the base directories and the python parser used for creating the JSON formatted file
RAW="/home/ooiuser/data/raw/$PLATFORM/$DEPLOY/extract"
PARSED="/home/ooiuser/data/parsed/$PLATFORM/$DEPLOY"
if [ ! -d $PARSED ]; then
    # Make the output directory, if it doesn't exist
    /bin/mkdir -p $PARSED
fi

# load the ooi python environment
source /home/ooiuser/miniconda/bin/activate ooi

# switch to the parser directory
cd /home/ooiuser/code/cgsn-parsers || exit

# Parse the data files based on the file type
case $FTYPE in
    "ACS" )
        # OPTAA data files
        OUT_DIR="$PARSED/optaa"
        if [ ! -d $OUT_DIR ]; then
            mkdir -p $OUT_DIR
        fi
        for file in "$RAW"/ucspp_*_ACS_ACS.txt; do
            out=$(basename $file)
            if [ ! -f $OUT_DIR/${out%.txt}.json ]; then
                echo "Parsing $file..."
                python -m cgsn_parsers.parsers.parse_cspp_optaa -i $file -o $OUT_DIR/${out%.txt}.json || echo "Failed to parse $file"
            fi
        done
        ;;

    "PPB" | "PPD" )
        # CTDPF data files
        OUT_DIR="$PARSED/ctdpf"
        if [ ! -d $OUT_DIR ]; then
            mkdir -p $OUT_DIR
        fi
        for file in "$RAW"/ucspp_*_"$FTYPE"_CTD.txt; do
            out=$(basename $file)
            if [ ! -f $OUT_DIR/${out%.txt}.json ]; then
                echo "Parsing $file..."
                python -m cgsn_parsers.parsers.parse_cspp_ctdpf -i $file -o $OUT_DIR/${out%.txt}.json || echo "Failed to parse $file"
            fi
        done

        # DOSTA data files
        OUT_DIR="$PARSED/dosta"
        if [ ! -d $OUT_DIR ]; then
            mkdir -p $OUT_DIR
        fi
        for file in "$RAW"/ucspp_*_"$FTYPE"_OPT.txt; do
            out=$(basename $file)
            if [ ! -f $OUT_DIR/${out%.txt}.json ]; then
                echo "Parsing $file..."
                python -m cgsn_parsers.parsers.parse_cspp_dosta -i $file -o $OUT_DIR/${out%.txt}.json || echo "Failed to parse $file"
            fi
        done

        # FLORT data files
        OUT_DIR="$PARSED/flort"
        if [ ! -d $OUT_DIR ]; then
            mkdir -p $OUT_DIR
        fi
        for file in "$RAW"/ucspp_*_"$FTYPE"_TRIP.txt; do
            out=$(basename $file)
            if [ ! -f $OUT_DIR/${out%.txt}.json ]; then
                echo "Parsing $file..."
                python -m cgsn_parsers.parsers.parse_cspp_flort -i $file -o $OUT_DIR/${out%.txt}.json || echo "Failed to parse $file"
            fi
        done

        # PARAD data files
        OUT_DIR="$PARSED/parad"
        if [ ! -d $OUT_DIR ]; then
            mkdir -p $OUT_DIR
        fi
        for file in "$RAW"/ucspp_*_"$FTYPE"_PARS.txt; do
            out=$(basename $file)
            if [ ! -f $OUT_DIR/${out%.txt}.json ]; then
                echo "Parsing $file..."
                python -m cgsn_parsers.parsers.parse_cspp_parad -i $file -o $OUT_DIR/${out%.txt}.json || echo "Failed to parse $file"
            fi
        done

        # SPKIR data files
        OUT_DIR="$PARSED/spkir"
        if [ ! -d $OUT_DIR ]; then
            mkdir -p $OUT_DIR
        fi
        for file in "$RAW"/ucspp_*_"$FTYPE"_OCR.txt; do
            out=$(basename $file)
            if [ ! -f $OUT_DIR/${out%.txt}.json ]; then
                echo "Parsing $file..."
                python -m cgsn_parsers.parsers.parse_cspp_spkir -i $file -o $OUT_DIR/${out%.txt}.json || echo "Failed to parse $file"
            fi
        done

        # VELPT data files
        OUT_DIR="$PARSED/velpt"
        if [ ! -d $OUT_DIR ]; then
            mkdir -p $OUT_DIR
        fi
        for file in "$RAW"/ucspp_*_"$FTYPE"_ADCP.txt; do
            out=$(basename $file)
            if [ ! -f $OUT_DIR/${out%.txt}.json ]; then
                echo "Parsing $file..."
                python -m cgsn_parsers.parsers.parse_cspp_velpt -i $file -o $OUT_DIR/${out%.txt}.json || echo "Failed to parse $file"
            fi
        done
        ;;

    "SNA" )
        # NUTNR data files
        OUT_DIR="$PARSED/nutnr"
        if [ ! -d $OUT_DIR ]; then
            mkdir -p $OUT_DIR
        fi
        for file in "$RAW"/ucspp_*_SNA_SNA.txt; do
            out=$(basename $file)
            if [ ! -f $OUT_DIR/${out%.txt}.json ]; then
                echo "Parsing $file..."
                python -m cgsn_parsers.parsers.parse_cspp_nutnr -i $file -o $OUT_DIR/${out%.txt}.json || echo "Failed to parse $file"
            fi
        done ;;

    "WC" )
        # HMR data files
        OUT_DIR="$PARSED/winch"
        if [ ! -d $OUT_DIR ]; then
            mkdir -p $OUT_DIR
        fi
        for file in "$RAW"/ucspp_*_WC_HMR.txt; do
            out=$(basename $file)
            if [ ! -f $OUT_DIR/${out%.txt}.json ]; then
                echo "Parsing $file..."
                python -m cgsn_parsers.parsers.parse_cspp_wc_hmr -i $file -o $OUT_DIR/${out%.txt}.json || echo "Failed to parse $file"
            fi
        done

        # SBE data files
        for file in "$RAW"/ucspp_*_WC_SBE.txt; do
            out=$(basename $file)
            if [ ! -f $OUT_DIR/${out%.txt}.json ]; then
                echo "Parsing $file..."
                python -m cgsn_parsers.parsers.parse_cspp_wc_sbe -i $file -o $OUT_DIR/${out%.txt}.json || echo "Failed to parse $file"
            fi
        done

        # WM data files
        for file in "$RAW"/ucspp_*_WC_WM.txt; do
            out=$(basename $file)
            if [ ! -f $OUT_DIR/${out%.txt}.json ]; then
                python -m cgsn_parsers.parsers.parse_cspp_wc_wm -i $file -o $OUT_DIR/${out%.txt}.json || echo "Failed to parse $file"
            fi
        done ;;

    * )
        echo "Unknown file type, please check the name again"
        exit 0 ;;
esac
