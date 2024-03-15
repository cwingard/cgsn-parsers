#!/bin/bash -e
#
# Parse the various data files for an Inshore Surface Mooring.
#
# C. Wingard 2015-04-17 -- Original Code
# C. Wingard 2024-03-12 -- Updated to use the new polling script

# Parse the command line inputs
if [ $# -ne 2 ]; then
    echo "$0: required inputs are the platform and deployment name"
    echo "     example: $0 ce01issm D00019"
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
./polling.sh "$HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY $assembly superv/cpm1" "$RAW/superv/*.superv.log"
./polling.sh "$HARVEST/harvest_gps.sh $PLATFORM $DEPLOY $assembly gps" "$RAW/gps/*.gps.log"
./polling.sh "$HARVEST/harvest_syslog_irid.sh $PLATFORM $DEPLOY $assembly irid" "$RAW/syslog/*.syslog.log"

dcl="dcl17" # Data logger for the instruments on the surface buoy
./polling.sh "$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY $assembly superv/$dcl" "$RAW/$dcl/superv/*.superv.log"
./polling.sh "$HARVEST/harvest_ctdbp.sh -f flort $PLATFORM $DEPLOY $assembly ctdbp" "$RAW/$dcl/ctdbp3/*.ctdbp3.log"
./polling.sh "$HARVEST/harvest_mopak.sh $PLATFORM $DEPLOY $assembly mopak" "$RAW/$dcl/mopak/*.mopak.log"
./polling.sh "$HARVEST/harvest_velpt.sh $PLATFORM $DEPLOY $assembly velpt" "$RAW/$dcl/velpt1/*.velpt1.log"

#### NSIF Instruments ####
assembly="nsif"  # midwater platform (no CPM or auxiliary instruments)
dcl="dcl16"  # Data logger for the instruments on the NSIF
./polling.sh "$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY $assembly superv/$dcl" "$RAW/$dcl/superv/*.superv.log"
./polling.sh "$HARVEST/harvest_ctdbp.sh -f dosta $PLATFORM $DEPLOY $assembly ctdbp" "$RAW/$dcl/ctdbp1/*.ctdbp1.log"
./polling.sh "$HARVEST/harvest_flort.sh $PLATFORM $DEPLOY $assembly flort" "$RAW/$dcl/flort/*.flort.log"
./polling.sh "$HARVEST/harvest_nutnr.sh -f suna $PLATFORM $DEPLOY $assembly nutnr" "$RAW/$dcl/nutnr/*.nutnr.log"
./polling.sh "$HARVEST/harvest_pco2w.sh $PLATFORM $DEPLOY $assembly pco2w" "$RAW/$dcl/pco2w1/*.pco2w1.log"
./polling.sh "$HARVEST/harvest_phsen.sh $PLATFORM $DEPLOY $assembly phsen" "$RAW/$dcl/phsen1/*.phsen1.log"
./polling.sh "$HARVEST/harvest_optaa.sh $PLATFORM $DEPLOY $assembly optaa" "$RAW/$dcl/optaa1/*.optaa1.log"
./polling.sh "$HARVEST/harvest_spkir.sh $PLATFORM $DEPLOY $assembly spkir" "$RAW/$dcl/spkir/*.spkir.log"
./polling.sh "$HARVEST/harvest_velpt.sh $PLATFORM $DEPLOY $assembly velpt" "$RAW/$dcl/velpt2/*.velpt2.log"

#### MFN Instruments ####
assembly="mfn"  # seafloor platform with CPM3 (no auxiliary instruments)
./polling.sh "$HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY $assembly superv/cpm3" "$RAW/cpm3/superv/*.superv.log"

dcl="dcl36"  # Data logger for a portion of the instruments on the MFN
./polling.sh "$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY $assembly superv/$dcl" "$RAW/$dcl/superv/*.superv.log"
./polling.sh "$HARVEST/harvest_adcp.sh -f pd0 $PLATFORM $DEPLOY $assembly adcp" "$RAW/$dcl/adcpt/*.adcpt.log"
./polling.sh "$HARVEST/harvest_pco2w.sh $PLATFORM $DEPLOY $assembly pco2w" "$RAW/$dcl/pco2w2/*.pco2w2.log"
./polling.sh "$HARVEST/harvest_phsen.sh $PLATFORM $DEPLOY $assembly phsen" "$RAW/$dcl/phsen2/*.phsen2.log"
./polling.sh "$HARVEST/harvest_presf.sh $PLATFORM $DEPLOY $assembly presf" "$RAW/$dcl/presf/*.presf.log"
./polling.sh "$HARVEST/harvest_vel3d.sh -f 8 $PLATFORM $DEPLOY $assembly vel3d" "$RAW/$dcl/vel3d/*.vel3d.log"

dcl="dcl37"  # Data logger for the remaining instruments on the MFN
./polling.sh "$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY $assembly superv/$dcl" "$RAW/$dcl/superv/*.superv.log"
./polling.sh "$HARVEST/harvest_ctdbp.sh -f dosta $PLATFORM $DEPLOY $assembly ctdbp" "$RAW/$dcl/ctdbp2/*.ctdbp2.log"
./polling.sh "$HARVEST/harvest_optaa.sh $PLATFORM $DEPLOY $assembly optaa" "$RAW/$dcl/optaa2/*.optaa2.log"
./polling.sh "$HARVEST/harvest_zplsc.sh $PLATFORM $DEPLOY $assembly zplsc" "$RAW/$dcl/zplsc/*.zplsc.log"
