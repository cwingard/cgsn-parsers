#!/usr/bin/bash -e
#
# Parse the various data files for a Coastal Pioneer Surface Mooring.
#
# Wingard, C. 2015-04-17

# Parse the command line inputs
if [ $# -ne 3 ]; then
    echo "$0: required inputs are the platform and deployment name, and"
    echo "the time flag for processing today's file (0) or N days prior"
    echo "     example: $0 cp01issm D00001 0"
    exit 1
fi
PLATFORM=${1,,}
DEPLOY=${2^^}
TIME="-$3 day"
FNAME=`/bin/date -u +%Y%m%d --date="$TIME"`

RAW="/home/ooiuser/data/raw"
HARVEST="/home/ooiuser/code/cgsn-parsers/utilities/harvesters"

# source the python environment for all subsequent processing
source /home/ooiuser/mambaforge/bin/activate ooi

# CPM1
echo "$HARVEST/harvest_syslog_gps.sh $PLATFORM $DEPLOY $FNAME.syslog.log"
$HARVEST/harvest_syslog_gps.sh $PLATFORM $DEPLOY $FNAME.syslog.log
echo "#$HARVEST/harvest_pwrsys.sh $PLATFORM $DEPLOY psc $FNAME.pwrsys.log"
#$HARVEST/harvest_pwrsys.sh $PLATFORM $DEPLOY psc $FNAME.pwrsys.log
echo "$HARVEST/harvest_syslog_irid.sh $PLATFORM $DEPLOY $FNAME.syslog.log"
$HARVEST/harvest_syslog_irid.sh $PLATFORM $DEPLOY $FNAME.syslog.log
echo "$HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY cpm1 buoy 1 $FNAME.syslog.log"
$HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY cpm1 buoy 1 $FNAME.syslog.log

# DCL11
echo "$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl11 buoy 1 $FNAME.syslog.log"
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl11 buoy 1 $FNAME.syslog.log
echo "$HARVEST/harvest_hydgn.sh $PLATFORM $DEPLOY dcl11 hyd1 $FNAME.hyd1.log"
$HARVEST/harvest_hydgn.sh $PLATFORM $DEPLOY dcl11 hyd1 $FNAME.hyd1.log
if [ $PLATFORM = "cp01cnsm" ]; then
    echo "$HARVEST/harvest_metbk.sh $PLATFORM $DEPLOY dcl11 metbk1 $FNAME.metbk1.log"
    $HARVEST/harvest_metbk.sh $PLATFORM $DEPLOY dcl11 metbk1 $FNAME.metbk1.log
else
    echo "$HARVEST/harvest_metbk.sh $PLATFORM $DEPLOY dcl11 metbk $FNAME.metbk.log"
    $HARVEST/harvest_metbk.sh $PLATFORM $DEPLOY dcl11 metbk $FNAME.metbk.log
fi
for mopak in $RAW/$PLATFORM/$DEPLOY/cg_data/dcl11/mopak/$FNAME*.mopak.log; do
    if [ -e $mopak ]; then
        SIZE=`du -k "$mopak" | cut -f1`
        if [ $SIZE -gt 0 ]; then
            echo "$HARVEST/harvest_mopak.sh $PLATFORM $DEPLOY dcl11 $mopak"
            $HARVEST/harvest_mopak.sh $PLATFORM $DEPLOY dcl11 $mopak
        fi
    fi
done

# DCL12
echo "$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl12 buoy 1 $FNAME.syslog.log"
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl12 buoy 1 $FNAME.syslog.log
echo "$HARVEST/harvest_fdchp.sh $PLATFORM $DEPLOY $FNAME.fdchp.log"
$HARVEST/harvest_fdchp.sh $PLATFORM $DEPLOY $FNAME.fdchp.log
echo "$HARVEST/harvest_hydgn.sh $PLATFORM $DEPLOY dcl12 hyd2 $FNAME.hyd2.log"
$HARVEST/harvest_hydgn.sh $PLATFORM $DEPLOY dcl12 hyd2 $FNAME.hyd2.log
if [ $PLATFORM = "cp01cnsm" ]; then
    echo "$HARVEST/harvest_metbk.sh $PLATFORM $DEPLOY dcl12 metbk2 $FNAME.metbk2.log"
    $HARVEST/harvest_metbk.sh $PLATFORM $DEPLOY dcl12 metbk2 $FNAME.metbk2.log
fi
echo "$HARVEST/harvest_pco2a.sh $PLATFORM $DEPLOY $FNAME.pco2a.log"
$HARVEST/harvest_pco2a.sh $PLATFORM $DEPLOY $FNAME.pco2a.log
echo "$HARVEST/harvest_wavss.sh $PLATFORM $DEPLOY $FNAME.wavss.log"
$HARVEST/harvest_wavss.sh $PLATFORM $DEPLOY $FNAME.wavss.log

# CPM2
echo "$HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY cpm2 nsif 1 $FNAME.syslog.log"
$HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY cpm2 nsif 1 $FNAME.syslog.log

# DCL26
echo "$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl26 nsif 1 $FNAME.syslog.log"
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl26 nsif 1 $FNAME.syslog.log
echo "$HARVEST/harvest_nutnr.sh $PLATFORM $DEPLOY dcl26 nutnr nsif suna $FNAME.nutnr.log"
$HARVEST/harvest_nutnr.sh $PLATFORM $DEPLOY dcl26 nutnr nsif suna $FNAME.nutnr.log
echo "$HARVEST/harvest_phsen.sh $PLATFORM $DEPLOY dcl26 phsen1 nsif $FNAME.phsen1.log"
$HARVEST/harvest_phsen.sh $PLATFORM $DEPLOY dcl26 phsen1 nsif $FNAME.phsen1.log
echo "$HARVEST/harvest_spkir.sh $PLATFORM $DEPLOY dcl26 spkir nsif $FNAME.spkir.log"
$HARVEST/harvest_spkir.sh $PLATFORM $DEPLOY dcl26 spkir nsif $FNAME.spkir.log
echo "$HARVEST/harvest_velpt.sh $PLATFORM $DEPLOY dcl26 velpt1 nsif $FNAME.velpt1.log"
$HARVEST/harvest_velpt.sh $PLATFORM $DEPLOY dcl26 velpt1 nsif $FNAME.velpt1.log

# DCL27
echo "$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl27 nsif 1 $FNAME.syslog.log"
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl27 nsif 1 $FNAME.syslog.log
echo "$HARVEST/harvest_ctdbp.sh $PLATFORM $DEPLOY dcl27 ctdbp1 nsif solo $FNAME.ctdbp1.log"
$HARVEST/harvest_ctdbp.sh $PLATFORM $DEPLOY dcl27 ctdbp1 nsif solo $FNAME.ctdbp1.log
echo "$HARVEST/harvest_dosta.sh $PLATFORM $DEPLOY dcl27 dosta1 nsif $FNAME.dosta1.log"
$HARVEST/harvest_dosta.sh $PLATFORM $DEPLOY dcl27 dosta1 nsif $FNAME.dosta1.log
echo "$HARVEST/harvest_flort.sh $PLATFORM $DEPLOY dcl27 flort nsif $FNAME.flort.log"
$HARVEST/harvest_flort.sh $PLATFORM $DEPLOY dcl27 flort nsif $FNAME.flort.log
for optaa in $RAW/$PLATFORM/$DEPLOY/cg_data/dcl27/optaa1*/$FNAME*.optaa1.log; do
    if [ -e $optaa ]; then
        SIZE=`du -k "$optaa" | cut -f1`
        if [ $SIZE -gt 0 ]; then
            echo "$HARVEST/harvest_optaa.sh $PLATFORM $DEPLOY dcl27 optaa1 nsif $optaa"
            $HARVEST/harvest_optaa.sh $PLATFORM $DEPLOY dcl27 optaa1 nsif $optaa
        fi
    fi
done

# CPM3
echo "$HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY cpm3 mfn 1 $FNAME.syslog.log"
$HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY cpm3 mfn 1 $FNAME.syslog.log
echo "#$HARVEST/harvest_pwrsys.sh $PLATFORM $DEPLOY mpea $FNAME.pwrsys.log"
#$HARVEST/harvest_pwrsys.sh $PLATFORM $DEPLOY mpea $FNAME.pwrsys.log

# DCL36
echo "$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl36 mfn 1 $FNAME.syslog.log"
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl36 mfn 1 $FNAME.syslog.log
echo "$HARVEST/harvest_adcp.sh $PLATFORM $DEPLOY dcl36 adcp mfn pd0 $FNAME.adcp.log"
$HARVEST/harvest_adcp.sh $PLATFORM $DEPLOY dcl36 adcp mfn pd0 $FNAME.adcp.log
echo "$HARVEST/harvest_pco2w.sh $PLATFORM $DEPLOY dcl36 pco2w mfn $FNAME.pco2w.log"
$HARVEST/harvest_pco2w.sh $PLATFORM $DEPLOY dcl36 pco2w mfn $FNAME.pco2w.log
echo "$HARVEST/harvest_phsen.sh $PLATFORM $DEPLOY dcl36 phsen2 mfn $FNAME.phsen2.log"
$HARVEST/harvest_phsen.sh $PLATFORM $DEPLOY dcl36 phsen2 mfn $FNAME.phsen2.log
echo "$HARVEST/harvest_presf.sh $PLATFORM $DEPLOY dcl36 $FNAME.presf.log"
$HARVEST/harvest_presf.sh $PLATFORM $DEPLOY dcl36 $FNAME.presf.log
echo "$HARVEST/harvest_velpt.sh $PLATFORM $DEPLOY dcl36 velpt2 mfn $FNAME.velpt1.log"
$HARVEST/harvest_velpt.sh $PLATFORM $DEPLOY dcl36 velpt2 mfn $FNAME.velpt1.log

# DCL37
echo "$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl37 mfn 1 $FNAME.syslog.log"
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl37 mfn 1 $FNAME.syslog.log
echo "$HARVEST/harvest_ctdbp.sh $PLATFORM $DEPLOY dcl37 ctdbp2 mfn solo $FNAME.ctdbp2.log"
$HARVEST/harvest_ctdbp.sh $PLATFORM $DEPLOY dcl37 ctdbp2 mfn solo $FNAME.ctdbp2.log
echo "$HARVEST/harvest_dosta.sh $PLATFORM $DEPLOY dcl37 dosta2 mfn $FNAME.dosta2.log"
$HARVEST/harvest_dosta.sh $PLATFORM $DEPLOY dcl37 dosta2 mfn $FNAME.dosta2.log
for optaa in $RAW/$PLATFORM/$DEPLOY/cg_data/dcl37/optaa2*/$FNAME*.optaa2.log; do
    if [ -e $optaa ]; then
        SIZE=`du -k "$optaa" | cut -f1`
        if [ $SIZE -gt 0 ]; then
            echo "$HARVEST/harvest_optaa.sh $PLATFORM $DEPLOY dcl37 optaa2 mfn $optaa"
            $HARVEST/harvest_optaa.sh $PLATFORM $DEPLOY dcl37 optaa2 mfn $optaa
        fi
    fi
done
echo "$HARVEST/harvest_zplsc.sh $PLATFORM $DEPLOY $FNAME.zplsc.log"
$HARVEST/harvest_zplsc.sh $PLATFORM $DEPLOY $FNAME.zplsc.log
