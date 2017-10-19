#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_cspp_flort
@file cgsn_parsers/parsers/parse_cspp_flort.py
@author Christopher Wingard
@brief Parses and converts the uncabled Coastal Surface Piercing Profiler -- ECO Triplet data files into a JSON file.
"""
import os
import re

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import FLOAT, INTEGER, NEWLINE, STRING, inputs

# Regex pattern for the ECO Triplet data from the uCSPP ECO Triplet data files
PATTERN = (
    FLOAT + r'\s+' + FLOAT + r'\s+' + STRING + r'\s+' +
    r'([0-9/]+[0-9]+\s+[0-9:]+[0-9]+)' + r'\s+' +
    INTEGER + r'\s+' + INTEGER + r'\s+' + INTEGER + r'\s+' + INTEGER + r'\s+' +
    INTEGER + r'\s+' + INTEGER + r'\s+' + INTEGER + r'\s+' +
    NEWLINE
)
REGEX = re.compile(PATTERN, re.DOTALL)

_parameter_names_flort = [
    'depth',
    'suspect_timestamp',
    'flort_date_time_string',
    'measurement_wavelength_beta',
    'raw_signal_beta',
    'measurement_wavelength_chl',
    'raw_signal_chl',
    'measurement_wavelength_cdom',
    'raw_signal_cdom',
    'raw_internal_temp'
]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the specific methods needed to parse the data, and
    extracts the data records from the uCSPP extracted data files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_flort)

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
        self.data.time.append(float(match.group(1)))
        self.data.depth.append(float(match.group(2)))
        self.data.suspect_timestamp.append(str(match.group(3)))
        self.data.flort_date_time_string.append(str(match.group(4)))
        self.data.measurement_wavelength_beta.append(int(match.group(5)))
        self.data.raw_signal_beta.append(int(match.group(6)))
        self.data.measurement_wavelength_chl.append(int(match.group(7)))
        self.data.raw_signal_chl.append(int(match.group(8)))
        self.data.measurement_wavelength_cdom.append(int(match.group(9)))
        self.data.raw_signal_cdom.append(int(match.group(10)))
        self.data.raw_internal_temp.append(int(match.group(11)))


def main(argv=None):
    # load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for flort
    flort = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    flort.load_ascii()
    flort.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(flort.data.toJSON())

if __name__ == '__main__':
    main()
