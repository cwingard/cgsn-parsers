#!/bin/bash -e
#
# Parse the various data files for an Inshore Surface Mooring.
#
# Wingard, C. 2015-04-17

# Parse the command line inputs
if [ $# -ne 3 ]; then
    echo "$0: required inputs are the platform and deployment name, and"
    echo "the time flag for processing today's file (0) or N days prior"
    echo "     example: $0 ce01issm D00001 0"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
TIME="-$3 day"
FNAME=`/bin/date -u +%Y%m%d --date="$TIME"`

RAW="/home/ooiuser/data/raw"
HARVEST="/home/ooiuser/code/cgsn-parsers/utilities/harvesters"
source activate ooi

# CPM1
$HARVEST/harvest_gps.sh $PLATFORM $DEPLOY $FNAME.gps.log
$HARVEST/harvest_syslog_irid.sh $PLATFORM $DEPLOY $FNAME.syslog.log
$HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY cpm1 buoy $FNAME.superv.log

# DCL17
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl17 buoy $FNAME.superv.log
$HARVEST/harvest_ctdbp.sh $PLATFORM $DEPLOY dcl17 ctdbp3 buoy flort $FNAME.ctdbp3.log
for mopak in $RAW/$PLATFORM/$DEPLOY/cg_data/dcl17/mopak/$FNAME*.mopak.log; do
    if [ -e $mopak ]; then
        SIZE=`du -k "$mopak" | cut -f1`
        if [ $SIZE -gt 0 ]; then
            $HARVEST/harvest_mopak.sh $PLATFORM $DEPLOY dcl17 $mopak
        fi
    fi
done
$HARVEST/harvest_velpt.sh $PLATFORM $DEPLOY dcl17 velpt1 buoy $FNAME.velpt1.log

# DCL16
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl16 nsif $FNAME.superv.log
$HARVEST/harvest_ctdbp.sh $PLATFORM $DEPLOY dcl16 ctdbp1 nsif dosta $FNAME.ctdbp1.log
$HARVEST/harvest_flort.sh $PLATFORM $DEPLOY dcl16 flort nsif $FNAME.flort.log
$HARVEST/harvest_nutnr.sh $PLATFORM $DEPLOY dcl16 nutnr nsif suna $FNAME.nutnr.log
$HARVEST/harvest_pco2w.sh $PLATFORM $DEPLOY dcl16 pco2w1 nsif $FNAME.pco2w1.log
$HARVEST/harvest_phsen.sh $PLATFORM $DEPLOY dcl16 phsen1 nsif $FNAME.phsen1.log
for optaa in $RAW/$PLATFORM/$DEPLOY/cg_data/dcl16/optaa1/$FNAME*.optaa1.log; do
    if [ -e $optaa ]; then
        SIZE=`du -k "$optaa" | cut -f1`
        if [ $SIZE -gt 0 ]; then
            $HARVEST/harvest_optaa.sh $PLATFORM $DEPLOY dcl16 optaa1 nsif $optaa
        fi
    fi
done
$HARVEST/harvest_spkir.sh $PLATFORM $DEPLOY dcl16 spkir nsif $FNAME.spkir.log
$HARVEST/harvest_velpt.sh $PLATFORM $DEPLOY dcl16 velpt2 nsif $FNAME.velpt2.log

# CPM3
$HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY cpm3 mfn $FNAME.superv.log

# DCL36
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl36 mfn $FNAME.superv.log
$HARVEST/harvest_adcp.sh $PLATFORM $DEPLOY dcl36 adcpt mfn pd0 $FNAME.adcpt.log
$HARVEST/harvest_pco2w.sh $PLATFORM $DEPLOY dcl36 pco2w2 mfn $FNAME.pco2w2.log
$HARVEST/harvest_phsen.sh $PLATFORM $DEPLOY dcl36 phsen2 mfn $FNAME.phsen2.log
$HARVEST/harvest_presf.sh $PLATFORM $DEPLOY dcl36 $FNAME.presf.log
for vel3d in $RAW/$PLATFORM/$DEPLOY/cg_data/dcl36/vel3d/$FNAME*.vel3d.log; do
    if [ -e $vel3d ]; then
        SIZE=`du -k "$vel3d" | cut -f1`
        if [ $SIZE -gt 0 ]; then
            $HARVEST/harvest_vel3d.sh $PLATFORM $DEPLOY dcl36 $vel3d
        fi
    fi
done

# DCL37
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl37 mfn $FNAME.superv.log
$HARVEST/harvest_ctdbp.sh $PLATFORM $DEPLOY dcl37 ctdbp2 mfn dosta $FNAME.ctdbp2.log
for optaa in $RAW/$PLATFORM/$DEPLOY/cg_data/dcl37/optaa2/$FNAME*.optaa2.log; do
    if [ -e $optaa ]; then
        SIZE=`du -k "$optaa" | cut -f1`
        if [ $SIZE -gt 0 ]; then
            $HARVEST/harvest_optaa.sh $PLATFORM $DEPLOY dcl37 optaa2 mfn $optaa
        fi
    fi
done
$HARVEST/harvest_zplsc.sh $PLATFORM $DEPLOY $FNAME.zplsc.log
