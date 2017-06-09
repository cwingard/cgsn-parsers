#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_cspp_spkir
@file cgsn_parsers/parsers/parse_cspp_spkir.py
@author Christopher Wingard
@brief Parses and converts the uncabled Coastal Surface Piercing Profiler -- CTD data files into a JSON file.
"""
import os
import re

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import FLOAT, INTEGER, NEWLINE, STRING, inputs

# Regex pattern for the CTD data from the uCSPP CTD data files
PATTERN = (
    FLOAT + r'\s+' +FLOAT + r'\s+' + STRING + r'\s+' +
    STRING + r'\s+' + INTEGER + r'\s+' + FLOAT + r'\s+' + INTEGER + r'\s+' +
    INTEGER + r'\s+' + INTEGER + r'\s+' + INTEGER + r'\s+' + INTEGER + r'\s+' +
    INTEGER + r'\s+' + INTEGER + r'\s+' + INTEGER + r'\s+' +
    INTEGER + r'\s+' + INTEGER + r'\s+' + INTEGER + r'\s+' + INTEGER + r'\s+' +
    r'[0-9A-F]{2}' + NEWLINE
)
REGEX = re.compile(PATTERN, re.DOTALL)

_parameter_names_spkir = [
    'depth',
    'suspect_timestamp',
    'serial_number',
    'timer',
    'sample_delay',
    'raw_channels',
    'input_voltage',
    'analog_rail_voltage',
    'frame_counter',
    'internal_temperature'
]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the specific methods needed to parse the data, and
    extracts the data records from the uCSPP extracted data files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_spkir)

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
        self.data.time.append(match.group(1))
        self.data.depth.append(match.group(2))
        self.data.suspect_timestamp.append(match.group(3))
        self.data.serial_number.append(match.group(5))
        self.data.timer.append(match.group(6))
        self.data.sample_delay.append(match.group(7))
        channels = [
            match.group(8), match.group(9), match.group(10), match.group(11),
            match.group(12), match.group(13), match.group(14)
        ]
        self.data.raw_channels.append(channels)
        self.data.input_voltage.append(match.group(15))
        self.data.analog_rail_voltage.append(match.group(16))
        self.data.internal_temperature.append(match.group(17))
        self.data.frame_counter.append(match.group(18))


if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for spkir
    spkir = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    spkir.load_ascii()
    spkir.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(spkir.data.toJSON())
