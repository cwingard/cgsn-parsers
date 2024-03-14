#!/bin/bash -e
#
# Parse the various data files for a Coastal Pioneer Surface Mooring.
#
# C. Wingard 2015-04-17 -- Original Code
# C. Wingard 2024-03-12 -- Updated to use the new polling script

# Parse the command line inputs
if [ $# -ne 2 ]; then
    echo "$0: required inputs are the platform and deployment name"
    echo "     example: $0 cp01cnsm D00016"
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
./polling.sh 30 "$HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY $assembly superv/cpm1" "$RAW/syslog/*.syslog.log"
./polling.sh 30 "$HARVEST/harvest_gps.sh $PLATFORM $DEPLOY $assembly gps" "$RAW/gps/*.gps.log"
./polling.sh 30 "$HARVEST/harvest_syslog_irid.sh $PLATFORM $DEPLOY $assembly irid" "$RAW/syslog/*.syslog.log"
./polling.sh 30 "$HARVEST/harvest_pwrsys.sh -f syslog $PLATFORM $DEPLOY $assembly psc" "$RAW/syslog/*.syslog.log"

dcl="dcl11"  # Data logger for a portion of the instruments on the surface buoy
./polling.sh 30 "$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY $assembly superv/$dcl" "$RAW/$dcl/syslog/*.syslog.log"
./polling.sh 30 "$HARVEST/harvest_hydgn.sh $PLATFORM $DEPLOY $assembly hyd1" "$RAW/$dcl/*.hyd1.log"
./polling.sh 30 "$HARVEST/harvest_mopak.sh $PLATFORM $DEPLOY $assembly mopak" "$RAW/$dcl/mopak/*.mopak.log"
if [ $PLATFORM = "cp01cnsm" ]; then
    ./polling.sh 30 "$HARVEST/harvest_metbk.sh $PLATFORM $DEPLOY $assembly metbk1" "$RAW/$dcl/*.metbk1.log"
else
    ./polling.sh 30 "$HARVEST/harvest_metbk.sh $PLATFORM $DEPLOY $assembly metbk" "$RAW/$dcl/*.metbk.log"
fi

dcl="dcl12"  # Data logger for the remaining instruments on the surface buoy
./polling.sh 30 "$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY $assembly superv/$dcl" "$RAW/$dcl/syslog/*.syslog.log"
./polling.sh 30 "$HARVEST/harvest_fdchp.sh $PLATFORM $DEPLOY $assembly fdchp" "$RAW/$dcl/fdchp/*.fdchp.log"
./polling.sh 30 "$HARVEST/harvest_hydgn.sh $PLATFORM $DEPLOY $assembly hyd2" "$RAW/$dcl/*.hyd2.log"
./polling.sh 30 "$HARVEST/harvest_pco2a.sh $PLATFORM $DEPLOY $assembly pco2a" "$RAW/$dcl/*.pco2a.log"
./polling.sh 30 "$HARVEST/harvest_wavss.sh $PLATFORM $DEPLOY $assembly wavss" "$RAW/$dcl/*.wavss.log"
if [ $PLATFORM = "cp01cnsm" ]; then
    ./polling.sh 30 "$HARVEST/harvest_metbk.sh $PLATFORM $DEPLOY $assembly metbk2" "$RAW/$dcl/*.metbk2.log"
fi

#### NSIF Instruments ####
assembly="nsif"  # midwater platform with CPM2 (no auxiliary instruments)
./polling.sh 30 "$HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY $assembly superv/cpm2" "$RAW/superv/*.superv.log"

dcl="dcl26"  # Data logger for a portion of the instruments on the NSIF
./polling.sh 30 "$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY $assembly superv/$dcl" "$RAW/$dcl/superv/*.superv.log"
./polling.sh 30 "$HARVEST/harvest_nutnr.sh -f suna $PLATFORM $DEPLOY $assembly nutnr" "$RAW/$dcl/nutnr/*.nutnr.log"
./polling.sh 30 "$HARVEST/harvest_phsen.sh $PLATFORM $DEPLOY $assembly phsen" "$RAW/$dcl/phsen*/*.phsen*.log"
./polling.sh 30 "$HARVEST/harvest_spkir.sh $PLATFORM $DEPLOY $assembly spkir" "$RAW/$dcl/spkir/*.spkir.log"
./polling.sh 30 "$HARVEST/harvest_velpt.sh $PLATFORM $DEPLOY $assembly velpt" "$RAW/$dcl/velpt*/*.velpt*.log"

dcl="dcl27"  # Data logger for the remaining instruments on the NSIF
./polling.sh 30 "$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY $assembly superv/$dcl" "$RAW/$dcl/superv/*.superv.log"
./polling.sh 30 "$HARVEST/harvest_ctdbp.sh -f solo $PLATFORM $DEPLOY $assembly ctdbp" "$RAW/$dcl/ctdbp*/*.ctdbp*.log"
./polling.sh 30 "$HARVEST/harvest_dosta.sh $PLATFORM $DEPLOY $assembly dosta" "$RAW/$dcl/dosta*/*.dosta*.log"
./polling.sh 30 "$HARVEST/harvest_flort.sh $PLATFORM $DEPLOY $assembly flort" "$RAW/$dcl/flort/*.flort.log"
./polling.sh 30 "$HARVEST/harvest_optaa.sh $PLATFORM $DEPLOY $assembly optaa" "$RAW/$dcl/optaa*/*.optaa*.log"

assembly="mfn"  # seafloor platform with CPM3 (and the MPEA)
./polling.sh 30 "$HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY $assembly superv/cpm3" "$RAW/cpm3/superv/*.superv.log"
./polling.sh 30 "$HARVEST/harvest_pwrsys.sh -f mpea $PLATFORM $DEPLOY $assembly mpea" "$RAW/cpm3/pwrsys/*.pwrsys.log"

dcl="dcl36"  # Data logger for a portion of the instruments on the MFN
./polling.sh 30 "$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY $assembly superv/$dcl" "$RAW/$dcl/superv/*.superv.log"
./polling.sh 30 "$HARVEST/harvest_adcp.sh -f pd0 $PLATFORM $DEPLOY $assembly adcp" "$RAW/$dcl/adcp*/*.adcp*.log"
./polling.sh 30 "$HARVEST/harvest_pco2w.sh $PLATFORM $DEPLOY $assembly pco2w" "$RAW/$dcl/pco2w*/*.pco2w*.log"
./polling.sh 30 "$HARVEST/harvest_phsen.sh $PLATFORM $DEPLOY $assembly phsen" "$RAW/$dcl/phsen*/*.phsen*.log"
./polling.sh 30 "$HARVEST/harvest_presf.sh $PLATFORM $DEPLOY $assembly presf" "$RAW/$dcl/presf/*.presf.log"
./polling.sh 30 "$HARVEST/harvest_velpt.sh $PLATFORM $DEPLOY $assembly velpt" "$RAW/$dcl/velpt*/*.velpt*.log"

dcl="dcl37"  # Data logger for the remaining instruments on the MFN
./polling.sh 30 "$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY $assembly superv/$dcl" "$RAW/$dcl/superv/*.superv.log"
./polling.sh 30 "$HARVEST/harvest_ctdbp.sh -f solo $PLATFORM $DEPLOY $assembly ctdbp" "$RAW/$dcl/ctdbp*/*.ctdbp*.log"
./polling.sh 30 "$HARVEST/harvest_dosta.sh $PLATFORM $DEPLOY $assembly dosta" "$RAW/$dcl/flort/*.flort.log"
./polling.sh 30 "$HARVEST/harvest_optaa.sh $PLATFORM $DEPLOY $assembly optaa" "$RAW/$dcl/optaa*/*.optaa*.log"
./polling.sh 30 "$HARVEST/harvest_zplsc.sh $PLATFORM $DEPLOY $assembly zplsc" "$RAW/$dcl/zplsc/*.zplsc.log"
