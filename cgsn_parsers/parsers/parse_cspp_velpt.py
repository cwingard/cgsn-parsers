#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_cspp_velpt
@file cgsn_parsers/parsers/parse_cspp_velpt.py
@author Christopher Wingard
@brief Parses and converts the uncabled Coastal Surface Piercing Profiler -- Aguadopp data files into a JSON file.
"""
import os
import re

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import FLOAT, INTEGER, NEWLINE, STRING, inputs

# Regex pattern for the Aguadopp data from the uCSPP Aguadopp data files
PATTERN = (
    FLOAT + r'\s+' + FLOAT + r'\s+' + STRING + r'\s+' +
    FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' +
    FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' +
    FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' +
    INTEGER + r'\s+' + INTEGER + r'\s+' + INTEGER + r'\s+' +
    NEWLINE
)
REGEX = re.compile(PATTERN, re.DOTALL)

_parameter_names_velpt = [
    'depth',
    'suspect_timestamp',
    'speed_of_sound',
    'heading',
    'pitch',
    'roll',
    'pressure',
    'temperature',
    'velocity_east',
    'velocity_north',
    'velocity_vertical',
    'amplitude_beam1',
    'amplitude_beam2',
    'amplitude_beam3'
]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the specific methods needed to parse the data, and
    extracts the data records from the uCSPP extracted data files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_velpt)

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
        self.data.speed_of_sound.append(match.group(4))
        self.data.heading.append(match.group(5))
        self.data.pitch.append(match.group(6))
        self.data.roll.append(match.group(7))
        self.data.pressure.append(match.group(8))
        self.data.temperature.append(match.group(9))
        self.data.velocity_east.append(match.group(10))
        self.data.velocity_north.append(match.group(11))
        self.data.velocity_vertical.append(match.group(12))
        self.data.amplitude_beam1.append(match.group(13))
        self.data.amplitude_beam2.append(match.group(14))
        self.data.amplitude_beam3.append(match.group(15))


if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for velpt
    velpt = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    velpt.load_ascii()
    velpt.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(velpt.data.toJSON())
