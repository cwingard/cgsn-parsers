#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_mpea
@file cgsn_parsers/parsers/parse_mpea.py
@author Christopher Wingard
@brief Parses the Power System data logged by the custom built WHOI data loggers.
"""
import os
import re

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLOAT, NEWLINE

# 2017/05/01 00:26:48.403 MPEA mpm: 373.58 50644.62 81000000 0C183060 cv1 1 23.98 569.23 cv2 0 0.00 0.00 cv3 0 0.00 0.00 cv4 0 0.00 0.00 cv5 0 0.00 0.00 cv6 0 0.00 0.00 cv7 0 0.00 0.00 aux 0 25281.11 1 htl 5.12 107.39 7.19 4.87 3792.2 7.56 2ad8

# Regex pattern for the MPEA power system records
PATTERN = (
    DCL_TIMESTAMP + r'\sMPEA\smpm:\s' +
    FLOAT + r'\s' + FLOAT + r'\s' +
    r'([0-9a-fA-F]{8})\s([0-9a-fA-F]{8})\s' +
    r'cv1\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'cv2\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'cv3\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'cv4\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'cv5\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'cv6\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'cv7\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'aux\s([0-1]{1})\s' + FLOAT + r'\s([0-1]{1})\s' +
    r'htl\s' + FLOAT + r'\s' + FLOAT + r'\s' + FLOAT + r'\s' + FLOAT + r'\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'([0-9a-f]{4})' + NEWLINE
)
REGEX = re.compile(PATTERN, re.DOTALL)

_parameter_names_mpea = [
    'date_time_string',
    'main_voltage',
    'main_current',
    'error_flag1',
    'error_flag2',
    'cv1_state',
    'cv1_voltage',
    'cv1_current',
    'cv2_state',
    'cv2_voltage',
    'cv2_current',
    'cv3_state',
    'cv3_voltage',
    'cv3_current',
    'cv4_state',
    'cv4_voltage',
    'cv4_current',
    'cv5_state',
    'cv5_voltage',
    'cv5_current',
    'cv6_state',
    'cv6_voltage',
    'cv6_current',
    'cv7_state',
    'cv7_voltage',
    'cv7_current',
    'auxiliary_state',
    'auxiliary_voltage',
    'auxiliary_current',
    'hotel_5v_voltage',
    'hotel_5v_current',
    'temperature',
    'relative_humidity',
    'leak_detect',
    'internal_pressure'
]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the MPEA specific
    methods to parse the data, and extracts the MPEA data records from the DCL
    daily log files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_mpea)

    def parse_data(self):
        """
        Iterate through the record lines (defined via the regex expression
        above) in the data object, and parse the data into a pre-defined
        dictionary object created using the Bunch class.
        """
        for line in self.raw:
            match = REGEX.match(line)
            if match:
                self._build_parsed_values(match)

    def _build_parsed_values(self, match):
        """
        Extract the data from the relevant regex groups and assign to elements
        of the data dictionary.
        """
        # Use the date_time_string to calculate an epoch timestamp (seconds since
        # 1970-01-01)
        epts = dcl_to_epoch(match.group(1))
        self.data.time.append(epts)
        self.data.date_time_string.append(str(match.group(1)))

        # Assign the remaining MET data to the named parameters
        self.data.main_voltage.append(float(match.group(2)))
        self.data.main_current.append(float(match.group(3)))
        self.data.error_flag1.append(str(match.group(4)))
        self.data.error_flag2.append(str(match.group(5)))
        self.data.cv1_state.append(int(match.group(6)))
        self.data.cv1_voltage.append(float(match.group(7)))
        self.data.cv1_current.append(float(match.group(8)))
        self.data.cv2_state.append(int(match.group(9)))
        self.data.cv2_voltage.append(float(match.group(10)))
        self.data.cv2_current.append(float(match.group(11)))
        self.data.cv3_state.append(int(match.group(12)))
        self.data.cv3_voltage.append(float(match.group(13)))
        self.data.cv3_current.append(float(match.group(14)))
        self.data.cv4_state.append(int(match.group(15)))
        self.data.cv4_voltage.append(float(match.group(16)))
        self.data.cv4_current.append(float(match.group(17)))
        self.data.cv5_state.append(int(match.group(18)))
        self.data.cv5_voltage.append(float(match.group(19)))
        self.data.cv5_current.append(float(match.group(20)))
        self.data.cv6_state.append(int(match.group(21)))
        self.data.cv6_voltage.append(float(match.group(22)))
        self.data.cv6_current.append(float(match.group(23)))
        self.data.cv7_state.append(int(match.group(24)))
        self.data.cv7_voltage.append(float(match.group(25)))
        self.data.cv7_current.append(float(match.group(26)))
        self.data.auxiliary_state.append(int(match.group(27)))
        self.data.auxiliary_voltage.append(float(match.group(28)))
        self.data.auxiliary_current.append(float(match.group(29)))
        self.data.hotel_5v_voltage.append(float(match.group(30)))
        self.data.hotel_5v_current.append(float(match.group(31)))
        self.data.temperature.append(float(match.group(32)))
        self.data.relative_humidity.append(float(match.group(33)))
        self.data.leak_detect.append(float(match.group(34)))
        self.data.internal_pressure.append(float(match.group(35)))


if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for MPEA
    mpea = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    mpea.load_ascii()
    mpea.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(mpea.data.toJSON())
