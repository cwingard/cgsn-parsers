#!/usr/bin/env bash
#
# Parse the various data files for a Global Surface Mooring.
#
# C. Wingard 2017-07-19 -- Original Code
# C. Wingard 2024-03-12 -- Updated to use the new polling script

# Parse the command line inputs
if [ $# -ne 2 ]; then
    echo "$0: required inputs are the platform and deployment name"
    echo "     example: $0 gi01sumo D00010"
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
./polling.sh "$HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY $assembly superv/cpm1" "$RAW/syslog/*.syslog.log"
./polling.sh "$HARVEST/harvest_gps.sh $PLATFORM $DEPLOY $assembly gps" "$RAW/gps/*.gps.log"
./polling.sh "$HARVEST/harvest_syslog_irid.sh $PLATFORM $DEPLOY $assembly irid" "$RAW/syslog/*.syslog.log"
./polling.sh "$HARVEST/harvest_pwrsys.sh -f syslog $PLATFORM $DEPLOY $assembly psc" "$RAW/syslog/*.syslog.log"

dcl="dcl11"  # Data logger for a portion of the instruments on the surface buoy
./polling.sh "$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY $assembly superv/$dcl" "$RAW/$dcl/syslog/*.syslog.log"
./polling.sh "$HARVEST/harvest_hydgn.sh $PLATFORM $DEPLOY $assembly hyd1" "$RAW/$dcl/hyd1/*.hyd1.log"
./polling.sh "$HARVEST/harvest_mopak.sh $PLATFORM $DEPLOY $assembly mopak" "$RAW/$dcl/mopak/*.mopak.log"
./polling.sh "$HARVEST/harvest_metbk.sh $PLATFORM $DEPLOY $assembly metbk1" "$RAW/$dcl/metbk1/*.metbk1.log"
./polling.sh "$HARVEST/harvest_dosta.sh $PLATFORM $DEPLOY $assembly dosta" "$RAW/$dcl/dosta1/*.dosta*.log"
./polling.sh "$HARVEST/harvest_nutnr.sh -f suna $PLATFORM $DEPLOY $assembly nutnr" "$RAW/$dcl/nutnr1/*.nutnr*.log"
./polling.sh "$HARVEST/harvest_spkir.sh $PLATFORM $DEPLOY $assembly spkir" "$RAW/$dcl/spkir1/*.spkir*.log"

dcl="dcl12"  # Data logger for the remaining instruments on the surface buoy
./polling.sh "$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY $assembly superv/$dcl" "$RAW/$dcl/syslog/*.syslog.log"
./polling.sh "$HARVEST/harvest_fdchp.sh $PLATFORM $DEPLOY $assembly fdchp" "$RAW/$dcl/fdchp/*.fdchp.log"
./polling.sh "$HARVEST/harvest_hydgn.sh $PLATFORM $DEPLOY $assembly hyd2" "$RAW/$dcl/hyd2/*.hyd2.log"
./polling.sh "$HARVEST/harvest_pco2a.sh $PLATFORM $DEPLOY $assembly pco2a" "$RAW/$dcl/pco2a/*.pco2a.log"
./polling.sh "$HARVEST/harvest_wavss.sh $PLATFORM $DEPLOY $assembly wavss" "$RAW/$dcl/wavss/*.wavss.log"
./polling.sh "$HARVEST/harvest_metbk.sh $PLATFORM $DEPLOY $assembly metbk2" "$RAW/$dcl/metbk2/*.metbk2.log"
./polling.sh "$HARVEST/harvest_flort.sh $PLATFORM $DEPLOY $assembly flort" "$RAW/$dcl/flort1/*.flort*.log"
./polling.sh "$HARVEST/harvest_optaa.sh $PLATFORM $DEPLOY $assembly optaa" "$RAW/$dcl/optaa1_decimated/*.optaa*.log"

#### NSIF Instruments ####
assembly="nsif"  # midwater platform (no CPM or auxiliary instruments)
dcl="dcl16"  # Data logger for the instruments on the NSIF
./polling.sh "$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY $assembly superv/$dcl" "$RAW/$dcl/syslog/*.syslog.log"
./polling.sh "$HARVEST/harvest_ctdbp.sh -f solo $PLATFORM $DEPLOY $assembly ctdbp" "$RAW/$dcl/ctdbp/*.ctdbp.log"
./polling.sh "$HARVEST/harvest_dosta.sh $PLATFORM $DEPLOY $assembly dosta" "$RAW/$dcl/dosta2/*.dosta*.log"
./polling.sh "$HARVEST/harvest_flort.sh $PLATFORM $DEPLOY $assembly flort" "$RAW/$dcl/flort2/*.flort*.log"
./polling.sh "$HARVEST/harvest_nutnr.sh -f suna $PLATFORM $DEPLOY $assembly nutnr" "$RAW/$dcl/nutnr2/*.nutnr*.log"
./polling.sh "$HARVEST/harvest_pco2w.sh $PLATFORM $DEPLOY $assembly pco2w" "$RAW/$dcl/pco2w/*.pco2w*.log"
./polling.sh "$HARVEST/harvest_optaa.sh $PLATFORM $DEPLOY $assembly optaa" "$RAW/$dcl/optaa2_decimated/*.optaa*.log"
./polling.sh "$HARVEST/harvest_spkir.sh $PLATFORM $DEPLOY $assembly spkir" "$RAW/$dcl/spkir2/*.spkir*.log"
./polling.sh "$HARVEST/harvest_velpt.sh $PLATFORM $DEPLOY $assembly velpt" "$RAW/$dcl/velpt/*.velpt*.log"

#### IMM hosted instruments (IMM controlled by DCL11) ####
assembly="imm"  # inductive modem
dcl="dcl11"  # Data logger for the IMM instruments
# the single ADCPS instrument (PD12 formatting)
./polling.sh "$HARVEST/harvest_imm_adcp.sh $PLATFORM $DEPLOY $assembly adcp" "$RAW/$dcl/$assembly/adcp/adcp*.DAT"
# the three CTDBP instruments
for i in $(seq -f "%02g" 1 3); do
    ./polling.sh "$HARVEST/harvest_imm_ctdbp.sh $PLATFORM $DEPLOY $assembly ctdbp$i" "$RAW/$dcl/$assembly/ctdbp$i/ctdbp*.DAT"
done
# the 10 CTDMO instruments
for i in $(seq -f "%02g" 1 10); do
    ./polling.sh "$HARVEST/harvest_imm_ctdmo.sh $PLATFORM $DEPLOY $assembly ctdmo$i" "$RAW/$dcl/$assembly/ctdmo$i/ctdmo*.DAT"
done
# the 3 PCO2W instruments
for i in $(seq 1 3); do
    ./polling.sh "$HARVEST/harvest_imm_pco2w.sh $PLATFORM $DEPLOY $assembly pco2w$i" "$RAW/$dcl/$assembly/pco2w$i/pco2w*.DAT"
done
# the 2 PHSEN instruments
for i in $(seq 1 2); do
    ./polling.sh "$HARVEST/harvest_imm_phsen.sh $PLATFORM $DEPLOY $assembly phsen$i" "$RAW/$dcl/$assembly/phsen$i/phsen*.DAT"
done
