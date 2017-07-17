#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_cspp_dosta
@file cgsn_parsers/parsers/parse_cspp_dosta.py
@author Christopher Wingard
@brief Parses and converts the uncabled Coastal Surface Piercing Profiler -- Optode data files into a JSON file.
"""
import numpy as np
import os
import re

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import FLOAT, INTEGER, NEWLINE, STRING, inputs

# Two regex patterns for the Optode data from the uCSPP Optode data files (with or without the percent saturation
PATTERN = (
    FLOAT + r'\s+' + FLOAT + r'\s+' + STRING + r'\s+' +
    INTEGER + r'\s+' + INTEGER + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' +
    FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' +
    FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' +
    NEWLINE
)
REGEX = re.compile(PATTERN, re.DOTALL)
PATTERN_SANS = (
    FLOAT + r'\s+' + FLOAT + r'\s+' + STRING + r'\s+' +
    INTEGER + r'\s+' + INTEGER + r'\s+' + FLOAT + r'\s+' +
    FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' +
    FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' +
    NEWLINE
)
REGEX_SANS = re.compile(PATTERN_SANS, re.DOTALL)

_parameter_names_dosta = [
    'depth',
    'suspect_timestamp',
    'product_number',
    'serial_number',
    'estimated_oxygen_concentration',
    'estimated_oxygen_saturation',
    'optode_temperature',
    'calibrated_phase',
    'temp_compensated_phase',
    'blue_phase',
    'red_phase',
    'blue_amplitude',
    'red_amplitude',
    'raw_temperature'
]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the specific methods needed to parse the data, and
    extracts the data records from the uCSPP extracted data files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_dosta)

    def parse_data(self):
        """
        Iterate through the record lines (defined via the regex expression
        above) in the data object, and parse the data into a pre-defined
        dictionary object created using the Bunch class.
        """
        for line in self.raw:
            match = REGEX.match(line)
            match_sans = REGEX_SANS.match(line)
            if match:
                self._build_parsed_values(match, True)

            if match_sans:
                self._build_parsed_values(match_sans, False)

    def _build_parsed_values(self, match, saturation):
        """
        Extract the data from the relevant regex groups and assign to elements
        of the data dictionary.
        """
        self.data.time.append(float(match.group(1)))
        self.data.depth.append(float(match.group(2)))
        self.data.suspect_timestamp.append(str(match.group(3)))
        self.data.product_number.append(int(match.group(4)))
        self.data.serial_number.append(int(match.group(5)))
        self.data.estimated_oxygen_concentration.append(float(match.group(6)))
        if saturation:
            self.data.estimated_oxygen_saturation.append(float(match.group(7)))
            self.data.optode_temperature.append(float(match.group(8)))
            self.data.calibrated_phase.append(float(match.group(9)))
            self.data.temp_compensated_phase.append(float(match.group(10)))
            self.data.blue_phase.append(float(match.group(11)))
            self.data.red_phase.append(float(match.group(12)))
            self.data.blue_amplitude.append(float(match.group(13)))
            self.data.red_amplitude.append(float(match.group(14)))
            self.data.raw_temperature.append(float(match.group(15)))
        else:
            self.data.estimated_oxygen_saturation.append(np.nan)
            self.data.optode_temperature.append(float(match.group(7)))
            self.data.calibrated_phase.append(float(match.group(8)))
            self.data.temp_compensated_phase.append(float(match.group(9)))
            self.data.blue_phase.append(float(match.group(10)))
            self.data.red_phase.append(float(match.group(11)))
            self.data.blue_amplitude.append(float(match.group(12)))
            self.data.red_amplitude.append(float(match.group(13)))
            self.data.raw_temperature.append(float(match.group(14)))


if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for dosta
    dosta = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    dosta.load_ascii()
    dosta.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(dosta.data.toJSON())
