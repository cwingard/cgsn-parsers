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
echo "$HARVEST/harvest_pwrsys.sh $PLATFORM $DEPLOY psc $FNAME.pwrsys.log"
$HARVEST/harvest_pwrsys.sh $PLATFORM $DEPLOY psc $FNAME.pwrsys.log
echo "$HARVEST/harvest_syslog_irid.sh $PLATFORM $DEPLOY $FNAME.syslog.log"
$HARVEST/harvest_syslog_irid.sh $PLATFORM $DEPLOY $FNAME.syslog.log
echo "$HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY cpm1 buoy 1 $FNAME.syslog.log"
$HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY cpm1 buoy 1 $FNAME.syslog.log

# DCL11
echo "$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl11 buoy 0 $FNAME.superv.log"
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl11 buoy 0 $FNAME.superv.log
echo "$HARVEST/harvest_hydgn.sh $PLATFORM $DEPLOY dcl11 hyd1 $FNAME.hyd1.log"
$HARVEST/harvest_hydgn.sh $PLATFORM $DEPLOY dcl11 hyd1 $FNAME.hyd1.log
echo "$HARVEST/harvest_metbk.sh $PLATFORM $DEPLOY dcl11 metbk1 $FNAME.metbk1.log"
$HARVEST/harvest_metbk.sh $PLATFORM $DEPLOY dcl11 metbk1 $FNAME.metbk1.log

# DCL12
echo "$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl12 buoy 0 $FNAME.superv.log"
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl12 buoy 0 $FNAME.superv.log
echo "$HARVEST/harvest_metbk.sh $PLATFORM $DEPLOY dcl12 metbk2 $FNAME.metbk2.log"
$HARVEST/harvest_metbk.sh $PLATFORM $DEPLOY dcl12 metbk2 $FNAME.metbk2.log
echo "$HARVEST/harvest_hydgn.sh $PLATFORM $DEPLOY dcl12 hyd2 $FNAME.hyd2.log"
$HARVEST/harvest_hydgn.sh $PLATFORM $DEPLOY dcl12 hyd2 $FNAME.hyd2.log
echo "$HARVEST/harvest_wavss.sh $PLATFORM $DEPLOY $FNAME.wavss.log"
$HARVEST/harvest_wavss.sh $PLATFORM $DEPLOY $FNAME.wavss.log

# DCL16
echo "$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl16 nsif 0 $FNAME.superv.log"
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl16 nsif 0 $FNAME.superv.log
echo "$HARVEST/harvest_flort.sh $PLATFORM $DEPLOY dcl16 flort1 nsif $FNAME.flort1.log"
$HARVEST/harvest_flort.sh $PLATFORM $DEPLOY dcl16 flort1 nsif $FNAME.flort1.log
echo "$HARVEST/harvest_ctdbp.sh $PLATFORM $DEPLOY dcl16 ctdbp1 nsif solo $FNAME.ctdbp1.log"
$HARVEST/harvest_ctdbp.sh $PLATFORM $DEPLOY dcl16 ctdbp1 nsif solo $FNAME.ctdbp1.log
echo "$HARVEST/harvest_velpt.sh $PLATFORM $DEPLOY dcl16 velpt1 nsif $FNAME.velpt1.log"
$HARVEST/harvest_velpt.sh $PLATFORM $DEPLOY dcl16 velpt1 nsif $FNAME.velpt1.log
echo "$HARVEST/harvest_turbid.sh $PLATFORM $DEPLOY dcl16 turbd nsif $FNAME.turbd.log"
$HARVEST/harvest_turbid.sh $PLATFORM $DEPLOY dcl16 turbd nsif $FNAME.turbd.log

# CPM3
echo "$HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY cpm3 mfn 1 $FNAME.syslog.log"
$HARVEST/harvest_superv_cpm.sh $PLATFORM $DEPLOY cpm3 mfn 1 $FNAME.syslog.log
echo "$HARVEST/harvest_pwrsys.sh $PLATFORM $DEPLOY mpea $FNAME.pwrsys.log"
$HARVEST/harvest_pwrsys.sh $PLATFORM $DEPLOY mpea $FNAME.pwrsys.log

# DCL36
echo "$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl36 mfn 0 $FNAME.superv.log"
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl36 mfn 0 $FNAME.superv.log
echo "$HARVEST/harvest_flort.sh $PLATFORM $DEPLOY dcl36 flort2 mfn $FNAME.flort2.log"
$HARVEST/harvest_flort.sh $PLATFORM $DEPLOY dcl36 flort2 mfn $FNAME.flort2.log

# DCL37
echo "$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl37 mfn 1 $FNAME.syslog.log"
$HARVEST/harvest_superv_dcl.sh $PLATFORM $DEPLOY dcl37 mfn 1 $FNAME.syslog.log
echo "$HARVEST/harvest_adcp.sh $PLATFORM $DEPLOY dcl37 adcp mfn pd0 $FNAME.adcp.log"
$HARVEST/harvest_adcp.sh $PLATFORM $DEPLOY dcl37 adcp mfn pd0 $FNAME.adcp.log
echo "$HARVEST/harvest_presf.sh $PLATFORM $DEPLOY dcl37 $FNAME.presf.log"
$HARVEST/harvest_presf.sh $PLATFORM $DEPLOY dcl37 $FNAME.presf.log
echo "$HARVEST/harvest_ctdbp.sh $PLATFORM $DEPLOY dcl37 ctdbp2 mfn solo $FNAME.ctdbp2.log"
$HARVEST/harvest_ctdbp.sh $PLATFORM $DEPLOY dcl37 ctdbp2 mfn solo $FNAME.ctdbp2.log
