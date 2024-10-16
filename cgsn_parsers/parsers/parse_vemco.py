#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_vemco
@file cgsn_parsers/parsers/parse_vemco.py
@author Christopher Wingard
@brief Parses VR2C data logged by the custom-built WHOI data loggers.
"""
import os
import pandas as pd
import re

from munch import Munch as Bunch
from calendar import timegm

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, INTEGER, FLOAT, NEWLINE

# Regex pattern for a line with a DCL time stamp and the VR2C status data
status = (
    DCL_TIMESTAMP + r'\s' + INTEGER + r',' +     # serial_number
    INTEGER + r',' +                             # sequence
    r'(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})' +  # VR2C Date and Time
    r',STS,DC=' + INTEGER + r',PC=' + INTEGER +  # detection and ping counts
    r',LV=' + FLOAT + r',BV=' + FLOAT +          # line and battery voltage
    r',BU=' + FLOAT + r',I=' + FLOAT +           # battery usage and current consumption
    r',T=' + FLOAT + r',DU=' + FLOAT +           # temperature and detection memory usage
    r',RU=' + FLOAT + r',XYZ=' +                 # raw memory usage and start of XYZ tilt data
    FLOAT + r':' + FLOAT + r':' + FLOAT +        # XYZ tilt data
    r',#([A-Z0-9]{2})' + NEWLINE                 # checksum
)
STATUS_REGEX = re.compile(status, re.DOTALL)

# Regex pattern for a line with a DCL time stamp and the VR2C tag detection data (covers both standard and sensor tags)
detections = (
    DCL_TIMESTAMP + r'\s' + INTEGER + r',' +     # serial_number
    INTEGER + r',' +                             # sequence
    r'(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})' +  # VR2C Date and Time
    r',([A-Z]\d{2}-\d{4}),(\d+|\d+,\d+)' +       # tag ID number and sensor data (if present)
    r',#([A-Z0-9]{2})' + NEWLINE                 # checksum
)
DETECTIONS_REGEX = re.compile(detections, re.DOTALL)


class ParameterNames(object):
    """
    Parameter names for the two data record types output by the VR2C.
    """
    def __init__(self):
        # status data
        self._status = [
            'time',
            'serial_number',
            'sequence',
            'vr2c_date_time',
            'detection_count',
            'ping_count',
            'line_voltage',
            'battery_voltage',
            'battery_usage',
            'current_consumption',
            'internal_temperature',
            'detection_memory_usage',
            'raw_memory_usage',
            'tilt_x',
            'tilt_y',
            'tilt_z'
        ]

        # tag detection data
        self._tags = [
            'vr2c_date_time',
            'serial_number',
            'sequence',
            'code_space',
            'tag_id',
            'sensor_data'
        ]

    # Create the initial dictionary object for the status and tag detection records.
    def create_dict(self):
        """
        Create a Bunch class object to store the parameter names for the status
        and tag detection data, with the data organized hierarchically by the
        data type.
        """
        bunch = Bunch()
        bunch.status = Bunch()
        bunch.tags = Bunch()

        for name in self._status:
            bunch.status[name] = []

        for name in self._tags:
            bunch.tags[name] = []

        return bunch


def _vr2c_date_time(time_string):
    """
    Convert the VR2C date and time string to an epoch timestamp (seconds since
    1970-01-01).
    """
    # convert file name date/time string to a pandas.Timestamp date/time object
    utc = pd.to_datetime(time_string, format='%Y-%m-%d %H:%M:%S', utc=True)

    # calculate the epoch time as seconds since 1970-01-01 in UTC
    epts = timegm(utc.timetuple())
    return epts


class Parser(object):
    """
    A Parser subclass that calls the Parser base class, adds the Vemco VR2C
    specific methods to parse the data, and extracts the VR2C data records from
    the DCL daily log files.
    """
    def __init__(self, infile):
        # set the infile names
        self.infile = infile

        # initialize the data dictionary using the parameter names defined above
        d = ParameterNames()
        self.data = d.create_dict()
        self.raw = None

    def load_vemco(self):
        """
        Create a buffered data object by opening the data file and reading in
        the contents as a single string
        """
        with open(self.infile, 'r', errors='ignore') as fid:
            self.raw = fid.read()

    def parse_status(self):
        """
        Iterate through the record markers (defined via the regex expressions
        above) in the data object, and parse the data file into a pre-defined
        dictionary object created using the Bunch class.
        """
        # find and parse the status data
        for match in re.finditer(STATUS_REGEX, self.raw):
            if match:
                self._build_parsed_status(match)

    def parse_tags(self):
        """
        Iterate through the record markers (defined via the regex expressions
        above) in the data object, and parse the data file into a pre-defined
        dictionary object created using the Bunch class.
        """
        # find and parse the tag detection data
        for match in re.finditer(DETECTIONS_REGEX, self.raw):
            if match:
                self._build_parsed_tags(match)

    def _build_parsed_status(self, match):
        """
        Extract the data from the relevant regex groups and assign to elements
        of the data dictionary.
        """
        # Use the date_time_string to calculate an epoch timestamp (seconds since
        # 1970-01-01)
        epts = dcl_to_epoch(match.group(1))
        self.data.status.time.append(epts)

        # Assign the remaining status data to the named parameters
        self.data.status.serial_number.append(int(match.group(2)))
        self.data.status.sequence.append(int(match.group(3)))
        self.data.status.vr2c_date_time.append(_vr2c_date_time(match.group(4)))
        self.data.status.detection_count.append(int(match.group(5)))
        self.data.status.ping_count.append(int(match.group(6)))
        self.data.status.line_voltage.append(float(match.group(7)))
        self.data.status.battery_voltage.append(float(match.group(8)))
        self.data.status.battery_usage.append(float(match.group(9)))
        self.data.status.current_consumption.append(float(match.group(10)))
        self.data.status.internal_temperature.append(float(match.group(11)))
        self.data.status.detection_memory_usage.append(float(match.group(12)))
        self.data.status.raw_memory_usage.append(float(match.group(13)))
        self.data.status.tilt_x.append(float(match.group(14)))
        self.data.status.tilt_y.append(float(match.group(15)))
        self.data.status.tilt_z.append(float(match.group(16)))

    def _build_parsed_tags(self, match):
        """
        Extract the data from the relevant regex groups and assign to elements
        of the data dictionary.
        """
        # Use the VR2C date_time_string to calculate an epoch timestamp (seconds since 1970-01-01). Don't use the DCL
        # time stamp for this since the VR2C time records when a detection occurred, not when the data was logged by
        # the DCL. Can use the DCL time stamp in the status packets to determine the VR2C clock offset and drift.
        self.data.tags.vr2c_date_time.append(_vr2c_date_time(match.group(4)))

        # Assign the remaining status data to the named parameters
        self.data.tags.serial_number.append(int(match.group(2)))
        self.data.tags.sequence.append(int(match.group(3)))
        self.data.tags.code_space.append(str(match.group(5)))
        tag_id = str(match.group(6)).split(',')  # tag_id[0] is the tag_id, tag_id[1] is the sensor data (if present)
        self.data.tags.tag_id.append(tag_id[0])
        if len(tag_id) > 1:
            self.data.tags.sensor_data.append(int(tag_id[1]))
        else:
            self.data.tags.sensor_data.append('-9999999')


def main(argv=None):
    # load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for vemco
    vemco = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    vemco.load_vemco()
    vemco.parse_status()
    vemco.parse_tags()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(vemco.data.toJSON())


if __name__ == '__main__':
    main()
