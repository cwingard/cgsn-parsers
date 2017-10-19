#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_cspp_wc_sbe
@file cgsn_parsers/parsers/parse_cspp_wc_sbe.py
@author Christopher Wingard
@brief Parses and converts the uncabled Coastal Surface Piercing Profiler -- WC data files into a JSON file.
"""
import os
import re

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import FLOAT, NEWLINE, STRING, inputs

# Regex pattern for the Winch Controller data from the uCSPP WC_SBE data files
PATTERN = (
    FLOAT + r'\s+' + STRING + r'\s+' + FLOAT + r'\s+' + FLOAT + NEWLINE
)
REGEX = re.compile(PATTERN, re.DOTALL)

_parameter_names_wc_sbe = [
    'suspect_timestamp',
    'pressure',
    'velocity'
    ]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the specific methods needed to parse the data, and
    extracts the data records from the uCSPP extracted data files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_wc_sbe)

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
        self.data.suspect_timestamp.append(str(match.group(2)))
        self.data.pressure.append(float(match.group(3)))
        self.data.velocity.append(float(match.group(4)))

def main(argv=None):
    # load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for wc_sbe
    wc_sbe = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    wc_sbe.load_ascii()
    wc_sbe.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(wc_sbe.data.toJSON())

if __name__ == '__main__':
    main()
