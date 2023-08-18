#!/usr/bin/bash -e
#
# Parse the various data files for the Global Irminger mooring
#
# Mario Carloni 2023-03-07

# Parse the command line inputs
if [ $# -ne 3 ]; then
    echo "$0: required inputs are the platform and deployment name, and"
    echo "the time flag for processing today's file (0) or N days prior"
    echo "     example: $0 gi01sumo D0009 0"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
TIME="-$3 day"
FNAME=`/bin/date -u +%Y%m%d --date="$TIME"`

# set the defalut paths for the raw data and the harvester scripts
RAW="/home/ooiuser/data/raw"
HARVEST="/home/ooiuser/code/cgsn-parsers/utilities/harvesters"

# source the python environment for all subsequent processing
source /home/ooiuser/mambaforge/bin/activate ooi

# CPM1
echo "$HARVEST/harvest_syslog_gps.sh $PLATFORM $DEPLOY $FNAME.syslog.log"
$HARVEST/harvest_syslog_gps.sh $PLATFORM $DEPLOY $FNAME.syslog.log
echo "#$HARVEST/harvest_pwrsys.sh $PLATFORM $DEPLOY $FNAME.pwrsys.log"
#$HARVEST/harvest_pwrsys.sh $PLATFORM $DEPLOY $FNAME.pwrsys.log
echo "$HARVEST/harvest_syslog_irid.sh $PLATFORM $DEPLOY $FNAME.syslog.log"
$HARVEST/harvest_syslog_irid.sh $PLATFORM $DEPLOY $FNAME.syslog.log
echo "$HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY cpm1 buoy 1 $FNAME.syslog.log"
$HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY cpm1 buoy 1 $FNAME.syslog.log

# DCL11
echo "$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl11 buoy 1 $FNAME.syslog.log"
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl11 buoy 1 $FNAME.syslog.log
echo "$HARVEST/harvest_hydgn.sh $PLATFORM $DEPLOY dcl11 hyd1 $FNAME.hyd1.log"
$HARVEST/harvest_hydgn.sh $PLATFORM $DEPLOY dcl11 hyd1 $FNAME.hyd1.log
echo "$HARVEST/harvest_metbk.sh $PLATFORM $DEPLOY dcl11 metbk1 $FNAME.metbk1.log"
$HARVEST/harvest_metbk.sh $PLATFORM $DEPLOY dcl11 metbk1 $FNAME.metbk1.log
for mopak in $RAW/$PLATFORM/$DEPLOY/cg_data/dcl11/mopak/$FNAME*.mopak.log; do
    if [ -e $mopak ]; then
        SIZE=`du -k "$mopak" | cut -f1`
        if [ $SIZE -gt 0 ]; then
            echo "$HARVEST/harvest_mopak.sh $PLATFORM $DEPLOY dcl11 $mopak"
            $HARVEST/harvest_mopak.sh $PLATFORM $DEPLOY dcl11 $mopak
        fi
    fi
done
echo "$HARVEST/harvest_dosta.sh $PLATFORM $DEPLOY dcl11 dosta1 buoy $FNAME.dosta1.log"
$HARVEST/harvest_dosta.sh $PLATFORM $DEPLOY dcl11 dosta1 buoy $FNAME.dosta1.log
echo "$HARVEST/harvest_nutnr.sh $PLATFORM $DEPLOY dcl11 nutnr1 buoy suna $FNAME.nutnr1.log"
$HARVEST/harvest_nutnr.sh $PLATFORM $DEPLOY dcl11 nutnr1 buoy suna $FNAME.nutnr1.log
echo "$HARVEST/harvest_spkir.sh $PLATFORM $DEPLOY dcl11 spkir1 buoy $FNAME.spkir1.log"
$HARVEST/harvest_spkir.sh $PLATFORM $DEPLOY dcl11 spkir1 buoy $FNAME.spkir1.log

# DCL12
echo "$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl12 buoy 1 $FNAME.syslog.log"
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl12 buoy 1 $FNAME.syslog.log
echo "$HARVEST/harvest_fdchp.sh $PLATFORM $DEPLOY $FNAME.fdchp.log"
$HARVEST/harvest_fdchp.sh $PLATFORM $DEPLOY $FNAME.fdchp.log
echo "$HARVEST/harvest_flort.sh $PLATFORM $DEPLOY dcl12 flort1 buoy $FNAME.flort1.log"
$HARVEST/harvest_flort.sh $PLATFORM $DEPLOY dcl12 flort1 buoy $FNAME.flort1.log
echo "$HARVEST/harvest_hydgn.sh $PLATFORM $DEPLOY dcl12 hyd2 $FNAME.hyd2.log"
$HARVEST/harvest_hydgn.sh $PLATFORM $DEPLOY dcl12 hyd2 $FNAME.hyd2.log
echo "$HARVEST/harvest_metbk.sh $PLATFORM $DEPLOY dcl12 metbk2 $FNAME.metbk2.log"
$HARVEST/harvest_metbk.sh $PLATFORM $DEPLOY dcl12 metbk2 $FNAME.metbk2.log
for optaa in $RAW/$PLATFORM/$DEPLOY/cg_data/dcl12/optaa1*/$FNAME*.optaa1.log; do
    if [ -e $optaa ]; then
        SIZE=`du -k "$optaa" | cut -f1`
        if [ $SIZE -gt 0 ]; then
            echo "$HARVEST/harvest_optaa.sh $PLATFORM $DEPLOY dcl12 optaa1 nsif $optaa"
            $HARVEST/harvest_optaa.sh $PLATFORM $DEPLOY dcl12 optaa1 nsif $optaa
        fi
    fi
done
echo "$HARVEST/harvest_pco2a.sh $PLATFORM $DEPLOY $FNAME.pco2a.log"
$HARVEST/harvest_pco2a.sh $PLATFORM $DEPLOY $FNAME.pco2a.log
echo "$HARVEST/harvest_wavss.sh $PLATFORM $DEPLOY $FNAME.wavss.log"
$HARVEST/harvest_wavss.sh $PLATFORM $DEPLOY $FNAME.wavss.log

# DCL16
echo "$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl16 nsif 1 $FNAME.syslog.log"
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl16 nsif 1 $FNAME.syslog.log
echo "$HARVEST/harvest_ctdbp.sh $PLATFORM $DEPLOY dcl16 ctdbp nsif solo $FNAME.ctdbp.log"
$HARVEST/harvest_ctdbp.sh $PLATFORM $DEPLOY dcl16 ctdbp nsif solo $FNAME.ctdbp.log
echo "$HARVEST/harvest_dosta.sh $PLATFORM $DEPLOY dcl16 dosta2 nsif $FNAME.dosta2.log"
$HARVEST/harvest_dosta.sh $PLATFORM $DEPLOY dcl16 dosta2 nsif $FNAME.dosta2.log
echo "$HARVEST/harvest_flort.sh $PLATFORM $DEPLOY dcl16 flort2 nsif $FNAME.flort2.log"
$HARVEST/harvest_flort.sh $PLATFORM $DEPLOY dcl16 flort2 nsif $FNAME.flort2.log
echo "$HARVEST/harvest_nutnr.sh $PLATFORM $DEPLOY dcl16 nutnr2 nsif suna $FNAME.nutnr2.log"
$HARVEST/harvest_nutnr.sh $PLATFORM $DEPLOY dcl16 nutnr2 nsif suna $FNAME.nutnr2.log
echo "$HARVEST/harvest_pco2w.sh $PLATFORM $DEPLOY dcl16 pco2w nsif $FNAME.pco2w.log"
$HARVEST/harvest_pco2w.sh $PLATFORM $DEPLOY dcl16 pco2w nsif $FNAME.pco2w.log
for optaa in $RAW/$PLATFORM/$DEPLOY/cg_data/dcl16/optaa2*/$FNAME*.optaa2.log; do
    if [ -e $optaa ]; then
        SIZE=`du -k "$optaa" | cut -f1`
        if [ $SIZE -gt 0 ]; then
            echo "$HARVEST/harvest_optaa.sh $PLATFORM $DEPLOY dcl16 optaa2 nsif $optaa"
            $HARVEST/harvest_optaa.sh $PLATFORM $DEPLOY dcl16 optaa2 nsif $optaa
        fi
    fi
done
echo "$HARVEST/harvest_spkir.sh $PLATFORM $DEPLOY dcl16 spkir2 nsif $FNAME.spkir2.log"
$HARVEST/harvest_spkir.sh $PLATFORM $DEPLOY dcl16 spkir2 nsif $FNAME.spkir2.log
echo "$HARVEST/harvest_velpt.sh $PLATFORM $DEPLOY dcl16 velpt nsif $FNAME.velpt.log"
$HARVEST/harvest_velpt.sh $PLATFORM $DEPLOY dcl16 velpt nsif $FNAME.velpt.log

##### IMM instruments logged via DCL11 #####
# If there is any ADCP data sent via the inductive modem, process it now
if [ -d $RAW/$PLATFORM/$DEPLOY/cg_data/dcl11/imm/adcp ]; then
    for adcp in $RAW/$PLATFORM/$DEPLOY/cg_data/dcl11/imm/adcp/adcp_$FNAME*.DAT; do
        if [ -e $adcp ]; then
            SIZE=`du -k "$adcp" | cut -f1`
            if [ $SIZE -gt 0 ]; then
                echo "$HARVEST/harvest_imm_adcp.sh $PLATFORM $DEPLOY $adcp"
                $HARVEST/harvest_imm_adcp.sh $PLATFORM $DEPLOY $adcp
            fi
        fi
    done
fi

# If there is any CTDBP data sent via the inductive modem, process it now
ls -d $RAW/$PLATFORM/$DEPLOY/cg_data/dcl11/imm/ctdbp*/ >/dev/null
if [ $? -eq 0 ]; then
    for ctdbp in $RAW/$PLATFORM/$DEPLOY/cg_data/dcl11/imm/ctdbp*/ctdbp*_$FNAME*.DAT; do
        if [ -e $ctdbp ]; then
            SIZE=`du -k "$ctdbp" | cut -f1`
            if [ $SIZE -gt 0 ]; then
                echo "$HARVEST/harvest_imm_ctdbp.sh $PLATFORM $DEPLOY $ctdbp"
                $HARVEST/harvest_imm_ctdbp.sh $PLATFORM $DEPLOY $ctdbp
            fi
        fi
    done
fi

# If there is any CTDMO data sent via the inductive modem, process it now
ls -d $RAW/$PLATFORM/$DEPLOY/cg_data/dcl11/imm/ctdmo* >/dev/null
if [ $? -eq 0 ]; then
    for ctdmo in $RAW/$PLATFORM/$DEPLOY/cg_data/dcl11/imm/ctdmo*/ctdmo*_$FNAME*.DAT; do
        if [ -e $ctdmo ]; then
            SIZE=`du -k "$ctdmo" | cut -f1`
            if [ $SIZE -gt 0 ]; then
                echo "$HARVEST/harvest_imm_ctdmo.sh $PLATFORM $DEPLOY $ctdmo"
                $HARVEST/harvest_imm_ctdmo.sh $PLATFORM $DEPLOY $ctdmo
            fi
        fi
    done
fi

# If there is any PCO2W data sent via the inductive modem, process it now
ls -d $RAW/$PLATFORM/$DEPLOY/cg_data/dcl11/imm/pco2w* >/dev/null
if [ $? -eq 0 ]; then
    for pco2w in $RAW/$PLATFORM/$DEPLOY/cg_data/dcl11/imm/pco2w*/pco2w*_$FNAME*.DAT; do
        if [ -e $pco2w ]; then
            SIZE=`du -k "$pco2w" | cut -f1`
            if [ $SIZE -gt 0 ]; then
                echo "$HARVEST/harvest_imm_pco2w.sh $PLATFORM $DEPLOY $pco2w"
                $HARVEST/harvest_imm_pco2w.sh $PLATFORM $DEPLOY $pco2w
            fi
        fi
    done
fi

# If there is any PHSEN data sent via the inductive modem, process it now
ls -d $RAW/$PLATFORM/$DEPLOY/cg_data/dcl11/imm/phsen* >/dev/null
if [ $? -eq 0 ]; then
    for phsen in $RAW/$PLATFORM/$DEPLOY/cg_data/dcl11/imm/phsen*/phsen*_$FNAME*.DAT; do
        if [ -e $phsen ]; then
            SIZE=`du -k "$phsen" | cut -f1`
            if [ $SIZE -gt 0 ]; then
                echo "$HARVEST/harvest_imm_phsen.sh $PLATFORM $DEPLOY $phsen"
                $HARVEST/harvest_imm_phsen.sh $PLATFORM $DEPLOY $phsen
            fi
        fi
    done
fi
