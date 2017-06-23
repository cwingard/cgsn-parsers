#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_cspp_optaa
@file cgsn_parsers/parsers/parse_cspp_optaa.py
@author Christopher Wingard
@brief Parses and converts the uncabled Coastal Surface Piercing Profiler -- AC-S data files into a JSON file.
"""
import os
import re

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import FLOAT, INTEGER, NEWLINE, STRING, inputs

# Regex pattern for the AC-S data from the uCSPP ACS data files
PATTERN = (
    r'^' + FLOAT + r'\s+' + FLOAT + r'\s+' + STRING + r'\s+' +
    INTEGER + r'\s+' + FLOAT + r'\s+' + INTEGER + r'\s+' +
    r'([\d\s]+)' + NEWLINE
)
REGEX = re.compile(PATTERN, re.DOTALL)

_parameter_names_optaa = [
    'depth',
    'suspect_timestamp',
    'serial_number',
    'elapsed_run_time',
    'num_wavelengths',
    'c_reference_dark',
    'c_reference_raw',
    'c_signal_dark',
    'c_signal_raw',
    'a_reference_dark',
    'a_reference_raw',
    'a_signal_dark',
    'a_signal_raw',
    'external_temp_raw',
    'internal_temp_raw',
    'pressure_raw'
]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the specific methods needed to parse the data, and
    extracts the data records from the uCSPP extracted data files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_optaa)

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
        self.data.serial_number.append(int(match.group(4)))
        self.data.elapsed_run_time.append(float(match.group(5)))

        # use the number of wavelengths to set the remaining arrays
        nwave = int(match.group(6))
        self.data.num_wavelengths.append(nwave)
        data = [int(i) for i in (match.group(7)).split()]

        # c and a channel references and signals for dark and raw measurements
        self.data.c_reference_dark.append(data[0])
        start = 1
        stop = start + nwave
        self.data.c_reference_raw.append(data[start:stop])
        self.data.c_signal_dark.append(data[stop])
        start = stop + 1
        stop = start + nwave
        self.data.c_signal_raw.append(data[start:stop])
        self.data.a_reference_dark.append(data[stop])
        start = stop + 1
        stop = start + nwave
        self.data.a_reference_raw.append(data[start:stop])
        self.data.a_signal_dark.append(data[stop])
        start = stop + 1
        stop = start + nwave
        self.data.a_signal_raw.append(data[start:stop])

        # external and internal raw temperatures and the external pressure
        self.data.external_temp_raw.append(data[-3])
        self.data.internal_temp_raw.append(data[-2])
        self.data.pressure_raw.append(data[-1])


if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for optaa
    optaa = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    optaa.load_ascii()
    optaa.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(optaa.data.toJSON())
