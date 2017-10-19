#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_mmp_coastal
@file cgsn_parsers/parsers/parse_mmp_coastal.py
@author Christopher Wingard
@brief Parses the Coastal MMP data files into a single JSON file.
"""
import datetime
import numpy as np
import os
import re

from munch import Munch as Bunch
from calendar import timegm
from pytz import timezone

# Import common utilities and base classes
from cgsn_parsers.parsers.common import INTEGER, FLOAT, NEWLINE, inputs

# Regex pattern for the engineering, PAR and ECO Triplet data from the 'E' files
EPATTERN = (
    r'\s+(\d{2}/\d{2}/\d{4}\s\d{2}:\d{2}:\d{2})' + r'\s+' +  # Date and Time String
    INTEGER + r'\s+' +          # motor current (mA)
    FLOAT + r'\s+' +            # battery voltage (V)
    FLOAT + r'\s+' +            # pressure (dbar)
    FLOAT + r'\s+' +            # raw PAR (mV)
    INTEGER + r'\s+' +          # raw backscatter (Beta) (counts)
    INTEGER + r'\s+' +          # raw chlorophyll (counts)
    INTEGER + r'\s*' +          # raw CDOM (counts)
    NEWLINE
)
EFILE_MATCHER = re.compile(EPATTERN, re.DOTALL)

# Regex pattern for the CTD and dissolved oxygen data from the 'C' files
CPATTERN = (
    FLOAT + r'\s+' +  # conductivity (mmho/cm)
    FLOAT + r'\s+' +  # temperature (degC)
    FLOAT + r'\s+' +  # pressure (dbar)
    INTEGER + r'\s+' +  # raw oxygen (Hz)
    NEWLINE
)
CFILE_MATCHER = re.compile(CPATTERN, re.DOTALL)

# Regex pattern for the Nortek Aquadopp II data from the 'A' files with the added beams information
APATTERN_BEAMS = (
    r'(\d{2}-\d{2}-\d{4}\s\d{2}:\d{2}:\d{2})' + r',' +  # Date and Time String
    FLOAT + r',' +          # temperature (degC)
    FLOAT + r',' +          # heading (degrees)
    FLOAT + r',' +          # pitch (degrees)
    FLOAT + r',' +          # roll (degrees)
    INTEGER + r',' +        # number of beams
    INTEGER + r',' +        # source for beam 0
    INTEGER + r',' +        # source for beam 1
    INTEGER + r',' +        # source for beam 2
    INTEGER + r',' +        # source for beam 3
    FLOAT + r',' +          # beam 0 velocity (m/s)
    FLOAT + r',' +          # beam 1 velocity (m/s)
    FLOAT + r',' +          # beam 2 velocity (m/s)
    INTEGER + r',' +        # amplitude beam 0 (counts)
    INTEGER + r',' +        # amplitude beam 1 (counts)
    INTEGER +               # amplitude beam 2 (counts)
    NEWLINE
)
ABEAMS_MATCHER = re.compile(APATTERN_BEAMS, re.DOTALL)

# Regex pattern for the Nortek Aquadopp II data from the 'A' files without the added beams information
APATTERN_SANS = (
    r'(\d{2}-\d{2}-\d{4}\s\d{2}:\d{2}:\d{2})' + r',' +  # Date and Time String
    FLOAT + r',' +          # temperature (degC)
    FLOAT + r',' +          # heading (degrees)
    FLOAT + r',' +          # pitch (degrees)
    FLOAT + r',' +          # roll (degrees)
    FLOAT + r',' +          # beam velocity 0 (m/s)
    FLOAT + r',' +          # beam velocity 1 (m/s)
    FLOAT + r',' +          # beam velocity 2 (m/s)
    INTEGER + r',' +        # amplitude beam 0 (counts)
    INTEGER + r',' +        # amplitude beam 1 (counts)
    INTEGER +               # amplitude beam 2 (counts)
    NEWLINE
)
ASANS_MATCHER = re.compile(APATTERN_SANS, re.DOTALL)

CODES = {
    'SMOOTH_RUNNING': 0,
    'MISSION_COMPLETE': 1,
    'OPERATOR_CTRL_C': 2,
    'TT8_COMM_FAILURE': 3,
    'CTD_COMM_FAILURE': 4,
    'ACM_COMM_FAILURE': 5,
    'TIMER_EXPIRED': 6,
    'MIN_BATTERY': 7,
    'AVG_MOTOR_CURRENT': 8,
    'MAX_MOTOR_CURRENT': 9,
    'SINGLE_PRESSURE': 10,
    'AVG_PRESSURE': 11,
    'AVG_TEMPERATURE': 12,
    'TOP_PRESSURE': 13,
    'BOTTOM_PRESSURE': 14,
    'RATE_ZERO': 15,
    'STOP_NULL': 16,
    'FLASH_CARD_FULL': 17,
    'FILE_SYSTEM_FULL': 18,
    'TOO_MANY_OPEN_FILES': 19,
    'AANDERAA_COMM_FAILURE': 20
}


class ParameterNames(object):
    """
    Parameter names for the three file types telemetered to shore from the McLane Profiler (MMP) via the Coastal
    Profiler mooring STC system. Additionally, creates parameters for a profile summary, equivalent to the contents
    in the TIMETAGS2.TXT file.
    """
    def __init__(self):
        # Profile Summary Data (equivalent to TIMETAGS2.TXT)
        self._profile = [
            'profile_id',
            'sensor_on',
            'motion_start',
            'motion_stop',
            'sensor_off',
            'ramp_status',
            'profile_status',
            'start_depth',
            'end_depth'
        ]

        # Engineering Data Record with raw PAR and ECO Triplet
        self._edata = [
            'time',
            'date_time_string',
            'motor_current',
            'battery_voltage',
            'pressure',
            'raw_par',
            'raw_scatter',
            'raw_chl',
            'raw_cdom'
        ]

        # CTD Data Record with raw O2
        self._cdata = [
            'time',
            'conductivity',
            'temperature',
            'pressure',
            'raw_oxygen'
        ]

        # Aquadopp II Data Record
        self._adata = [
            'time',
            'date_time_string',
            'temperature',
            'heading',
            'pitch',
            'roll',
            'beams',
            'beam_0_velocity',
            'beam_1_velocity',
            'beam_2_velocity',
            'amplitude_beam_0',
            'amplitude_beam_1',
            'amplitude_beam_2'
        ]

    # Create the initial dictionary object from the velocity, diagnostics and
    # diagnostics data header data types.
    def create_dict(self):
        """
        Create a Bunch class object to store the parameter names for the McClane MMP profiler used on the Coastal
        Surface moorings, with the data organized hierarchically by the data type.
        """
        bunch = Bunch()
        bunch.profile = Bunch()
        bunch.edata = Bunch()
        bunch.cdata = Bunch()
        bunch.adata = Bunch()

        for name in self._profile:
            bunch.profile[name] = []

        for name in self._edata:
            bunch.edata[name] = []

        for name in self._cdata:
            bunch.cdata[name] = []

        for name in self._adata:
            bunch.adata[name] = []

        return bunch


class Parser(object):
    """
    A Parser class, with methods to load, parse the data, and save to JSON the MMP data on a profile-by-profile basis.
    """
    def __init__(self, efile, cfile, afile):
        # set the infile names
        self.efile = efile
        self.cfile = cfile
        self.afile = afile

        # initialize the data dictionary using the parameter names defined above
        data = ParameterNames()
        self.data = data.create_dict()
        self.eraw = None
        self.craw = None
        self.araw = None
        self._beams = None

    def load_ascii(self):
        """
        Create a buffered data object by opening the data file and reading in
        the contents
        """
        with open(self.efile, 'r') as fid:
            self.eraw = fid.readlines()

        with open(self.cfile, 'r') as fid:
            self.craw = fid.readlines()

        if os.path.isfile(self.afile):
            with open(self.afile, 'r') as fid:
                self.araw = fid.readlines()

    def parse_edata(self):
        """
        Iterate through the record markers (defined via the regex expression above) in the data object, and parse the
        data file into a pre-defined dictionary object created using the Bunch class.
        """
        # first parse all the engineering, ECO Triplet and PAR data
        for line in self.eraw:
            match = EFILE_MATCHER.match(line)
            if match:
                self._build_parsed_edata(match)

        # use the above parsed data and summary data in the file to update the summary profile dictionary
        self.data.profile.profile_id = int(self.eraw[2].split()[1])

        dt = datetime.datetime.strptime(' '.join(self.eraw[4].split()[-2:]), '%m/%d/%Y %H:%M:%S')
        dt.replace(tzinfo=timezone('UTC'))
        self.data.profile.sensor_on = timegm(dt.timetuple())

        dt = datetime.datetime.strptime(' '.join(self.eraw[5].split()[-2:]), '%m/%d/%Y %H:%M:%S')
        dt.replace(tzinfo=timezone('UTC'))
        self.data.profile.motion_start = timegm(dt.timetuple())

        dt = datetime.datetime.strptime(' '.join(self.eraw[-2].split()[-2:]), '%m/%d/%Y %H:%M:%S')
        dt.replace(tzinfo=timezone('UTC'))
        self.data.profile.motion_stop = timegm(dt.timetuple())

        dt = datetime.datetime.strptime(' '.join(self.eraw[-1].split()[-2:]), '%m/%d/%Y %H:%M:%S')
        dt.replace(tzinfo=timezone('UTC'))
        self.data.profile.sensor_off = timegm(dt.timetuple())

        self.data.profile.ramp_status = CODES['_'.join(self.eraw[-5].split()[-2:])]
        self.data.profile.profile_status = CODES['_'.join(self.eraw[-4].split()[-2:])]

        self.data.profile.start_depth = [db for _, db in enumerate(self.data.edata.pressure) if db != 0.0][0]
        self.data.profile.end_depth = self.data.edata.pressure[-1]

    def parse_cdata(self):
        """
        Iterate through the record markers (defined via the regex expression above) in the data object, and parse the
        data file into a pre-defined dictionary object created using the Bunch class.
        """
        # first parse all the CTD and oxygen data
        for line in self.craw:
            match = CFILE_MATCHER.match(line)
            if match:
                self._build_parsed_cdata(match)

        # now we need to create a time record, since the CTD record does not include an explicit time stamp
        idx = np.flipud(np.arange(len(self.data.cdata.pressure)))
        self.data.cdata.time = (self.data.profile.sensor_on - idx).tolist()

    def parse_adata(self):
        """
        Iterate through the record markers (defined via the regex expression above) in the data object, and parse the
        data file into a pre-defined dictionary object created using the Bunch class.
        """
        for line in self.araw:
            # ideally the unit was configured to output the beams information, so we know how to convert the beam
            # velocity data to the Earth coordinate frame.
            beams = ABEAMS_MATCHER.match(line)
            if beams:
                self._build_parsed_adata(beams, True)
            else:
                # For those early deployment cases where the beams info was not included, we need to determine which
                # way the profiler was travelling and assign a default beams array. This is fairly straight forward
                # operation, since we can use the start and end depths from the engineering data to determine our
                # direction of travel.
                sans = ASANS_MATCHER.match(line)
                if sans:
                    if (self.data.profile.start_depth - self.data.profile.end_depth) > 0:
                        self._beams = [3, 1, 2, 4, 0]
                    else:
                        self._beams = [3, 2, 3, 4, 0]
                    self._build_parsed_adata(sans, False)

        # now we need to recreate the time record, since the Aquadopp II record does not include an explicit time stamp
        idx = np.arange(len(self.data.adata.time))
        tic = 1 / np.round((len(self.data.adata.time) / (np.size(np.where(np.diff(self.data.adata.time) == 1)) + 1)))
        epts = self.data.adata.time[0]
        self.data.adata.time = (epts + (idx * tic)).tolist()

    def _build_parsed_edata(self, match):
        """
        Extract the data from the relevant regex groups and assign to elements of the data dictionary.
        """
        # Use the date_time_string to calculate an epoch timestamp (seconds since 1970-01-01)
        dt = datetime.datetime.strptime(match.group(1), '%m/%d/%Y %H:%M:%S')
        utc = dt.replace(tzinfo=timezone('UTC'))
        self.data.edata.time.append(timegm(utc.timetuple()))
        self.data.edata.date_time_string.append(str(match.group(1)))

        # Assign the remaining data to the named parameters
        self.data.edata.motor_current.append(int(match.group(2)))
        self.data.edata.battery_voltage.append(float(match.group(3)))
        self.data.edata.pressure.append(float(match.group(4)))
        self.data.edata.raw_par.append(float(match.group(5)))
        self.data.edata.raw_scatter.append(int(match.group(6)))
        self.data.edata.raw_chl.append(int(match.group(7)))
        self.data.edata.raw_cdom.append(int(match.group(8)))

    def _build_parsed_cdata(self, match):
        """
        Extract the data from the relevant regex groups and assign to elements of the data dictionary.
        """
        self.data.cdata.conductivity.append(float(match.group(1)))
        self.data.cdata.temperature.append(float(match.group(2)))
        self.data.cdata.pressure.append(float(match.group(3)))
        self.data.cdata.raw_oxygen.append(int(match.group(4)))

    def _build_parsed_adata(self, match, beams):
        """
        Extract the data from the relevant regex groups and assign to elements of the data dictionary.
        """
        dt = datetime.datetime.strptime(match.group(1), '%m-%d-%Y %H:%M:%S')
        utc = dt.replace(tzinfo=timezone('UTC'))
        self.data.adata.time.append(timegm(utc.timetuple()))
        self.data.adata.date_time_string.append(str(match.group(1)))

        self.data.adata.temperature.append(float(match.group(2)))
        self.data.adata.heading.append(float(match.group(3)))
        self.data.adata.pitch.append(float(match.group(4)))
        self.data.adata.roll.append(float(match.group(5)))
        if beams:   # beams data is included in the data set
            self.data.adata.beams.append([int(match.group(i)) for i in range(6, 11)])
            self.data.adata.beam_0_velocity.append(float(match.group(11)))
            self.data.adata.beam_1_velocity.append(float(match.group(12)))
            self.data.adata.beam_2_velocity.append(float(match.group(13)))
            self.data.adata.amplitude_beam_0.append(int(match.group(14)))
            self.data.adata.amplitude_beam_1.append(int(match.group(15)))
            self.data.adata.amplitude_beam_2.append(int(match.group(16)))
        else:   # apply a pre-determined beams array based on direction of profiler travel
            self.data.adata.beams.append(self._beams)
            self.data.adata.beam_0_velocity.append(float(match.group(6)))
            self.data.adata.beam_1_velocity.append(float(match.group(7)))
            self.data.adata.beam_2_velocity.append(float(match.group(8)))
            self.data.adata.amplitude_beam_0.append(int(match.group(9)))
            self.data.adata.amplitude_beam_1.append(int(match.group(10)))
            self.data.adata.amplitude_beam_2.append(int(match.group(11)))


def main(argv=None):
    # load the input arguments
    args = inputs(argv)
    efile = os.path.abspath(args.infile)
    cfile = os.path.join(os.path.dirname(efile), re.sub('E', 'C', os.path.basename(efile)))
    afile = os.path.join(os.path.dirname(efile), re.sub('E', 'A', os.path.basename(efile)))
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for the MMP
    mmp = Parser(efile, cfile, afile)

    # load the data into buffered objects and parse the data into dictionaries
    mmp.load_ascii()
    mmp.parse_edata()
    mmp.parse_cdata()
    if mmp.araw:
        mmp.parse_adata()

    # write the resulting Bunch object via the toJSON method to a JSON formatted data file
    with open(outfile, 'w') as f:
        f.write(mmp.data.toJSON())

if __name__ == '__main__':
    main()
