#!/usr/bin/env bash
#
# Parse the various data files for a Global Surface Mooring.
#
# Wingard, C. 2017-07-19

# Parse the command line inputs
if [ $# -ne 3 ]; then
    echo "$0: required inputs are the platform and deployment name, and"
    echo "the time flag for processing today's file (0) or N days prior"
    echo "     example: $0 ga01sumo D00001 0"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
TIME="-$3 day"
FNAME=`/bin/date -u +%Y%m%d --date="$TIME"`

RAW="/home/ooiuser/data/raw"
HARVEST="/home/ooiuser/code/cgsn-parsers/utilities/harvesters"

# CPM1
$HARVEST/harvest_gps.sh $PLATFORM $DEPLOY $FNAME.gps.log
$HARVEST/harvest_pwrsys.sh $PLATFORM $DEPLOY $FNAME.pwrsys.log
$HARVEST/harvest_syslog_fb250.sh $PLATFORM $DEPLOY $FNAME.syslog.log
$HARVEST/harvest_syslog_irid.sh $PLATFORM $DEPLOY $FNAME.syslog.log
$HARVEST/harvest_syslog_rda.sh $PLATFORM $DEPLOY $FNAME.syslog.log
$HARVEST/harvest_pwrsys.sh $PLATFORM $DEPLOY $FNAME.pwrsys.log
#$HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY cpm1 buoy 0 $FNAME.superv.log

# DCL11
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl11 buoy $FNAME.superv.log
$HARVEST/harvest_hydgn.sh $PLATFORM $DEPLOY dcl11 hyd1 $FNAME.hyd1.log
$HARVEST/harvest_metbk.sh $PLATFORM $DEPLOY dcl11 metbk1 $FNAME.metbk1.log
for mopak in $RAW/$PLATFORM/$DEPLOY/cg_data/dcl11/mopak/$FNAME*.mopak.log; do
    if [ -e $mopak ]; then
        SIZE=`du -k "$mopak" | cut -f1`
        if [ $SIZE -gt 0 ]; then
            $HARVEST/harvest_mopak.sh $PLATFORM $DEPLOY dcl11 $mopak
        fi
    fi
done
$HARVEST/harvest_dosta.sh $PLATFORM $DEPLOY dcl11 dosta1 buoy $FNAME.dosta1.log
$HARVEST/harvest_nutnr.sh $PLATFORM $DEPLOY dcl11 nutnr1 buoy 1 $FNAME.nutnr1.log
$HARVEST/harvest_spkir.sh $PLATFORM $DEPLOY dcl11 spkir1 buoy $FNAME.spkir1.log

# DCL12
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl12 buoy $FNAME.superv.log
$HARVEST/harvest_fdchp.sh $PLATFORM $DEPLOY $FNAME.fdchp.log
$HARVEST/harvest_flort.sh $PLATFORM $DEPLOY dcl12 flort1 buoy $FNAME.flort1.log
$HARVEST/harvest_hydgn.sh $PLATFORM $DEPLOY dcl12 hyd2 $FNAME.hyd2.log
$HARVEST/harvest_metbk.sh $PLATFORM $DEPLOY dcl12 metbk2 $FNAME.metbk2.log
for optaa in $RAW/$PLATFORM/$DEPLOY/cg_data/dcl12/optaa1/$FNAME*.optaa1.log; do
    if [ -e $optaa ]; then
        SIZE=`du -k "$optaa" | cut -f1`
        if [ $SIZE -gt 0 ]; then
            $HARVEST/harvest_optaa.sh $PLATFORM $DEPLOY dcl12 optaa1 nsif $optaa
        fi
    fi
done
$HARVEST/harvest_pco2a.sh $PLATFORM $DEPLOY $FNAME.pco2a.log
$HARVEST/harvest_wavss.sh $PLATFORM $DEPLOY $FNAME.wavss.log

# DCL16
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl16 nsif $FNAME.superv.log
$HARVEST/harvest_ctdbp.sh $PLATFORM $DEPLOY dcl16 ctdbp nisf 1 $FNAME.ctdbp.log
$HARVEST/harvest_dosta.sh $PLATFORM $DEPLOY dcl16 dosta2 buoy $FNAME.dosta2.log
$HARVEST/harvest_flort.sh $PLATFORM $DEPLOY dcl16 flort2 nsif $FNAME.flort2.log
$HARVEST/harvest_nutnr.sh $PLATFORM $DEPLOY dcl16 nutnr2 nsif 1 $FNAME.nutnr2.log
$HARVEST/harvest_pco2w.sh $PLATFORM $DEPLOY dcl16 pco2w nsif $FNAME.pco2w.log
for optaa in $RAW/$PLATFORM/$DEPLOY/cg_data/dcl16/optaa2/$FNAME*.optaa2.log; do
    if [ -e $optaa ]; then
        SIZE=`du -k "$optaa" | cut -f1`
        if [ $SIZE -gt 0 ]; then
            $HARVEST/harvest_optaa.sh $PLATFORM $DEPLOY dcl16 optaa2 nsif $optaa
        fi
    fi
done
$HARVEST/harvest_spkir.sh $PLATFORM $DEPLOY dcl16 spkir2 nsif $FNAME.spkir2.log
$HARVEST/harvest_velpt.sh $PLATFORM $DEPLOY dcl16 velpt nsif $FNAME.velpt.log

# IMM hosted instruments via DCL11
# If there is any ADCP data sent via the inductive modem, process it now
if [ -d $RAW/$PLATFORM/$DEPLOY/dcl11/imm/adcp ]; then
    for adcp in $RAW/$PLATFORM/$DEPLOY/imm/adcp/adcp_$FNAME*.DAT; do
        if [ -e $adcp ]; then
            SIZE=`du -k "$adcp" | cut -f1`
            if [ $SIZE -gt 0 ]; then
                $HARVEST/harvest_imm_adcp.sh $PLATFORM $DEPLOY $adcp
            fi
        fi
    done
fi

# If there is any CTDBP data sent via the inductive modem, process it now
if [ -d $RAW/$PLATFORM/$DEPLOY/dcl11/imm/ctdbp* ]; then
    for ctdbp in $RAW/$PLATFORM/$DEPLOY/imm/ctdbp*/ctdbp*_$FNAME*.DAT; do
        if [ -e $ctdbp ]; then
            SIZE=`du -k "$ctdbp" | cut -f1`
            if [ $SIZE -gt 0 ]; then
                $HARVEST/harvest_imm_ctdbp.sh $PLATFORM $DEPLOY $ctdbp
            fi
        fi
    done
fi

# If there is any CTDMO data sent via the inductive modem, process it now
if [ -d $RAW/$PLATFORM/$DEPLOY/dcl11/imm/ctdmo* ]; then
    for ctdmo in $RAW/$PLATFORM/$DEPLOY/imm/ctdmo*/ctdmo*_$FNAME*.DAT; do
        if [ -e $ctdmo ]; then
            SIZE=`du -k "$ctdmo" | cut -f1`
            if [ $SIZE -gt 0 ]; then
                $HARVEST/harvest_imm_ctdmo.sh $PLATFORM $DEPLOY $ctdmo
            fi
        fi
    done
fi

# If there is any PCO2W data sent via the inductive modem, process it now
if [ -d $RAW/$PLATFORM/$DEPLOY/dcl11/imm/pco2w* ]; then
    for pco2w in $RAW/$PLATFORM/$DEPLOY/imm/pco2w*/pco2w*_$FNAME*.DAT; do
        if [ -e $pco2w ]; then
            SIZE=`du -k "$pco2w" | cut -f1`
            if [ $SIZE -gt 0 ]; then
                $HARVEST/harvest_imm_pco2w.sh $PLATFORM $DEPLOY $pco2w
            fi
        fi
    done
fi

# If there is any PHSEN data sent via the inductive modem, process it now
if [ -d $RAW/$PLATFORM/$DEPLOY/dcl11/imm/phsen* ]; then
    for phsen in $RAW/$PLATFORM/$DEPLOY/imm/phsen*/phsen*_$FNAME*.DAT; do
        if [ -e $phsen ]; then
            SIZE=`du -k "$phsen" | cut -f1`
            if [ $SIZE -gt 0 ]; then
                $HARVEST/harvest_imm_phsen.sh $PLATFORM $DEPLOY $phsen
            fi
        fi
    done
fi