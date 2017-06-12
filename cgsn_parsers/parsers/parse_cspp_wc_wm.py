#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_cspp_wc_wm
@file cgsn_parsers/parsers/parse_cspp_wc_wm.py
@author Christopher Wingard
@brief Parses and converts the uncabled Coastal Surface Piercing Profiler -- WC_WM data files into a JSON file.
"""
import os
import re

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import FLOAT, INTEGER, NEWLINE, STRING, inputs

# Regex pattern for the Winch Controller data from the uCSPP WC_WM data files
PATTERN = (
    FLOAT + r'\s+' + FLOAT + r'\s+' + STRING + r'\s+' +
    INTEGER + r'\s+' + FLOAT + r'\s+' + STRING + r'\s+' +
    INTEGER + r'\s+' + INTEGER + r'\s+' + FLOAT + r'\s+' +
    INTEGER + r'\s+' + INTEGER + r'\s+' + FLOAT + NEWLINE
)
REGEX = re.compile(PATTERN, re.DOTALL)

_parameter_names_wc_wm = [
    'depth',
    'suspect_timestamp',
    'encoder_counts',
    'current',
    'status_string',
    'raw_velocity',
    'temperature',
    'voltage',
    'raw_time',
    'raw_discharge',
    'rope_on_drum'
    ]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the specific methods needed to parse the data, and
    extracts the data records from the uCSPP extracted data files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_wc_wm)

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
        self.data.encoder_counts.append(match.group(4))
        self.data.current.append(match.group(5))
        self.data.status_string.append(match.group(6))
        self.data.raw_velocity.append(match.group(7))
        self.data.temperature.append(match.group(8))
        self.data.voltage.append(match.group(9))
        self.data.raw_time.append(match.group(10))
        self.data.raw_discharge.append(match.group(11))
        self.data.rope_on_drum.append(match.group(12))


if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for wc_wm
    wc_wm = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    wc_wm.load_ascii()
    wc_wm.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(wc_wm.data.toJSON())
