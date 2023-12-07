#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_ifcb_hdr
@file cgsn_parsers/parsers/parse_ifcb_hdr.py
@author Paul Whelan
@brief Parses McLean IFCB ascii header data files produced by the IFCB instrument
"""
import os
import re
import pandas as pd
from calendar import timegm

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLOAT,  NEWLINE

# Regex pattern for extracting datetime from filename
FNAME_DTIME_PATTERN = (
    r'\w(\d\d\d\d\d\d\d\dT\d\d\d\d\d\d)_' +
    r'.+' +
    NEWLINE
  )
FNAME_DTIME = re.compile( FNAME_DTIME_PATTERN, re.DOTALL )

# Regex pattern for a line with a name value pair separated by ': '
# Value can be ascii or numeric, as determined by the corresponding name
PATTERN = (
    r'(.+):\s' +                          # Name
    r'(.+)' +                             # Value
    NEWLINE
)
REGEX = re.compile(PATTERN, re.DOTALL)

# Store param names in dictionary with values of corresponding data type

_param_names_ifcb_dict = {
#    'SoftwareVersion': '0.0.0.0',
#    'AnalogFirmware': 11,
#    'HousekeepingFirmware': 11,
    'sampleNumber': 11,
    'sampleType': 'Normal',
    'triggerCount': 1111,
    'roiCount': 1111,
    'humidity': 11.1,
    'temperature': 11.11,
    'runTime': 1111.11111111,
    'inhibitTime': 111.11111,
#    'ADCFileFormat': 'trigger#, ADCtime, PMTA, PMTB, PMTC, PMTD, PeakA, PeakB, PeakC, PeakD, TimeOfFlight, GrabTimeStart, GrabTimeEnd, RoiX, RoiY, RoiWidth, RoiHeight, StartByte, ComparatorOut, StartPoint, SignalLength, Status, RunTime, InhibitTime',
#    'DAQ_MCCserialPort_DAC_MCConly': '/dev/ttyS1',
#    'auxPower1': 'False',
#    'autoStart': 'False',
#    'InteractiveAutoStart': 'False',
#    'autoShutdown': 'False',
#    'HumidityAlarmThreshold(%)': 11,
#    'ValveHumidityHysteresis_DAC_MCConly': 111,
#    'FanTemperatureThreshold_DAC_MCConly': 11111,
#    'FanTemperatureHysteresis_DAC_MCConly': 111,
#    'valveDelay': 111,
#    'FlashlampControlVoltage': 1.1111,
#    'HKTRIGGERtoFlashlampDelayTime_x434ns_DAC_MCConly': 111,
#    'FlashlampPulseLength_x434ns_DAC_MCConly': 11,
#    'CameraPulseLength_x434ns_DAC_MCConly': 111,
#    'cameraGain': 1,
#    'binarizeThreshold': 1,
#    'minimumBlobArea': 1111,
#    'blobXgrowAmount': 11,
#    'blobYgrowAmount': 11,
#    'minimumGapBewtweenAdjacentBlobs': 11,
#    'laserState': 'True',
#    'runningCamera': 'True',
    'pump1State': 'True',
    'pump2State': 'False',
#    'stirrer': 'False',
#    'viewImages': 'True',
#    'viewRoisOnly': 'False',
#    'sendTriggerContent': 'False',
#    'triggerContinuous': 'False',
#    'continuousTriggerRate': 1,
#    'fill3newSheathState': 'False',
#    'PMTAtriggerThreshold_DAQ_MCConly': 0.11,
#    'PMTBtriggerThreshold_DAQ_MCConly': 0.11,
#    'PMTCtriggerThreshold_DAQ_MCConly': 1,
#    'PMTDtriggerThreshold_DAQ_MCConly': 1,
#    'ADCdataRateDAQ_MCConly': 111,
#    'integratorSettleTime': 1,
#    'PMTtriggerSelection_DAQ_MCConly': 1,
#    'altPMTtriggerSelection_DAQ_MCConly': 1,
#    'ADCPGA_DAQ_MCConly': 1,
#    'triggerAckTimeout_x34720ns_DAQ_MCConly': 11111,
#    'TimeoutForFirstFrame': 11,
#    'pulseStretchTime_x2170ns_DAQ_MCConly': 11,
#    'maximumPulseLength_x2170ns_DAQ_MCConly': 1111,
#    'hasCamera': 'True',
#    'liveEnvironment': 'False',
#    'flash': 'True',
    'PMTAhighVoltage': 0.1,
    'PMTBhighVoltage': 0.1,
#    'intervalBetweenAlternateHardwareSettings': 1,
    'Alt_FlashlampControlVoltage': 1,
    'pumpDriveVoltage': 11,
    'altPMTAHighVoltage': 0.11,
    'altPMTBHighVoltage': 0.11,
#    'altPMTATriggerThreshold_DAQ_MCConly': 0.11,
#    'altPMTBTriggerThreshold_DAQ_MCConly': 0.11,
#    'viewTriggers': 'False',
#    'viewGraphs': 'True',
#    'viewActivity': 'True',
#    'viewFPS': 'True',
#    'KloehnPort': '/dev/ttyUSB0',
    'syringeSamplingSpeed': 11,
    'syringeOffset': 1111,
    'NumberSyringesToAutoRun': 1111,
    'SyringeSampleVolume': 1,
    'altSyringeSampleVolume': 1,
    'sampleVolume2skip': 1,
#    'syringeSize': 1,
#    'primeVolume': 1,
#    'flushVolume': 1,
#    'BleachVolume': 1,
#    'BiocideVolume': 1,
#    'stepsToFullSyringe': 111,
#    'debubbleWithSample': 'True',
#    'RefillAfterDebubble': 'True',
#    'primeSampleTube': 'False',
#    'backflushWithSample': 'False',
#    'runBeads': 'False',
#    'runSampleFast': 'False',
#    'BeadsSampleVolume': 0.1,
#    'NumberSyringesBetweenBeadsRun': 1,
#    'NumberSyringesBetweenCleaningRun': 1,
#    'RunFastFactor': 1,
#    'viewSyringe': 'True',
#    'viewValve': 'True',
    'focusMotorSmallStep_ms': 11,
    'focusMotorLargeStep_ms': 111,
    'laserMotorSmallStep_ms': 111,
    'laserMotorLargeStep_ms': 1111
#    'debubbleConeVolume': 1,
#    'debubbleNeedleVolume': 1,
#    'debubbleRefillVolume': 1.1,
#    'debubbleLeftVolume': 0.1,
#    'BleachRinseCount': 1,
#    'BleachRinseVolume': 1,
#    'BleachToExhaust': 'False',
#    'SamplingFastSpeed': 1,
#    'CounterCleaning': 111,
#    'CounterBeads': 111,
#    'CounterAlt': 111,
#    'imagerID': 111,
#    'DataFilePath': '/mnt/data/ifcbdata',
#    'FolderHierarchy': 'False',
#    'OutputFiles': 'True',
#    'FileComment': 'file comment',
#    'triggerThreadCount': 1,
#    'featureThreadCount': 1,
#    'FeaturesVersion': 'V4',
#    'featureGeneration': 'False',
#    'SaveBlobs': 'False',
#    'WebBrowser': 'chromium',
#    'WebBrowserArguments': '--disable-gpu',
#    'GPSFeed': 1,
#    'PhytoArmDataSource': 1,
#    'ServerAsAdmin': 'False',
#    'HostAsAdmin': 'False',
#    'UpdateServer': 'http://mclanelabs.dyndns.org:8082/external/update/ifcbacquire/release/'
    }

# _parameter_names_ifcb = _param_names_ifcb_dict.keys();



class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the rbr presf specific
    methods to parse the data, and extracts the rbr presf data records from the DCL
    daily log files.
    """
    def __init__(self, infile):
        self.initialize(infile, list(_param_names_ifcb_dict.keys()) )

    def parse_data(self):
        """
        Get the time value from the file name, then...
        Iterate through the record lines (defined via the regex expression
        above) in the data object, and parse the data into a pre-defined
        dictionary object created using the Bunch class.
        """
        match = FNAME_DTIME.match( os.path.basename(self.infile) )
        if match:
            # convert file name date/time string to seconds since 1970-01-01 in UTC
            utc = pd.to_datetime( match.group(1), format='%Y%m%dT%H%M%S', utc=True)
            epts = timegm(utc.timetuple())
            self.data.time.append( epts )
        
        for line in self.raw:
            match = REGEX.match(line)
            if match:
                self._build_parsed_values(match)

    def _build_parsed_values(self, match):
        """
        Extract the data from the relevant regex groups and assign to elements
        of the data dictionary.
        """

        # Get name value pair, then match to known parameters for value typing
        var_name = match.group(1)
        str_value = match.group(2).strip('\n')

        if var_name in _param_names_ifcb_dict.keys() :

            if isinstance( _param_names_ifcb_dict[ var_name ], int ) :
                self.data[ var_name ].append( int(str_value) )

            elif isinstance( _param_names_ifcb_dict[ var_name ], float ) :
                self.data[ var_name ].append( float(str_value) )

            else :
                self.data[ var_name ].append( str_value )
        

def main(argv=None):
    # load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for ifcb header
    ifcb = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    ifcb.load_ascii()
    ifcb.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write( ifcb.data.toJSON() )

if __name__ == '__main__':
    main()
