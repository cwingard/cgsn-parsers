#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_cspp_nutnr
@file cgsn_parsers/parsers/parse_cspp_nutnr.py
@author Christopher Wingard
@brief Parses and converts the uncabled Coastal Surface Piercing Profiler -- SUNA data files into a JSON file.
"""
import os
import re

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import FLOAT, INTEGER, NEWLINE, STRING, inputs

# Regex pattern for the SUNA data (light frames only) from the uCSPP SNA data files
PATTERN = (
    r'^' + FLOAT + r'\s+' + FLOAT + r'\s+' + STRING + r'\s+' +
    STRING + r'\s+' + INTEGER + r'\s+' + INTEGER + r'\s+' +
    FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' +
    FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' +
    INTEGER + r'\s+' + INTEGER + r'\s+' + INTEGER + r'\s+' +
    r'(([+-]?[0-9]+\s){256})' +
    FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' + INTEGER + r'\s+' +
    FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' +
    FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' +
    INTEGER + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' +
    r'[0-9A-F]{2}' + NEWLINE
)
REGEX = re.compile(PATTERN, re.DOTALL)

_parameter_names_nutnr = [
    'depth',
    'suspect_timestamp',
    'measurement_type',
    'year',
    'day_of_year',
    'decimal_hours',
    'nitrate_concentration',
    'nitrogen_in_nitrate',
    'absorbance_254',
    'absorbance_250',
    'bromide_trace',
    'spectal_average',
    'dark_value',
    'integration_factor',
    'channel_measurements',
    'temperature_internal',
    'temperature_spectrometer',
    'temperature_lamp',
    'lamp_on_time',
    'humidity',
    'voltage_main',
    'voltage_lamp',
    'voltage_internal',
    'main_current',
    'fit_auxiliary_1',
    'fit_auxiliary_2',
    'fit_base_1',
    'fit_base_2',
    'fit_rmse'
]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the specific methods needed to parse the data, and
    extracts the data records from the uCSPP extracted data files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_nutnr)

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
        self.data.measurement_type.append(str(match.group(4)))
        self.data.year.append(int(match.group(5)))
        self.data.day_of_year.append(int(match.group(6)))
        self.data.decimal_hours.append(float(match.group(7)))
        self.data.nitrate_concentration.append(float(match.group(8)))
        self.data.nitrogen_in_nitrate.append(float(match.group(9)))
        self.data.absorbance_254.append(float(match.group(10)))
        self.data.absorbance_250.append(float(match.group(11)))
        self.data.bromide_trace.append(float(match.group(12)))
        self.data.spectal_average.append(int(match.group(13)))
        self.data.dark_value.append(int(match.group(14)))
        self.data.integration_factor.append(int(match.group(15)))
        channels = [int(i) for i in (match.group(16)).split()]
        self.data.channel_measurements.append(channels)
        self.data.temperature_internal.append(float(match.group(18)))
        self.data.temperature_spectrometer.append(float(match.group(19)))
        self.data.temperature_lamp.append(float(match.group(20)))
        self.data.lamp_on_time.append(int(match.group(21)))
        self.data.humidity.append(float(match.group(22)))
        self.data.voltage_main.append(float(match.group(23)))
        self.data.voltage_lamp.append(float(match.group(24)))
        self.data.voltage_internal.append(float(match.group(25)))
        self.data.main_current.append(float(match.group(26)))
        self.data.fit_auxiliary_1.append(float(match.group(27)))
        self.data.fit_auxiliary_2.append(float(match.group(28)))
        self.data.fit_base_1.append(float(match.group(29)))
        self.data.fit_base_2.append(float(match.group(30)))
        self.data.fit_rmse.append(float(match.group(31)))


if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for nutnr
    nutnr = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    nutnr.load_ascii()
    nutnr.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(nutnr.data.toJSON())
