#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_suna
@file cgsn_parsers/parsers/parse_suna.py
@author Christopher Wingard
@brief Parses SUNA data logged by the custom built WHOI data loggers.
"""
import os
import re

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLOAT, INTEGER, STRING, NEWLINE

# Set regex string to just find the SUNA data.
PATTERN = (
    DCL_TIMESTAMP + r'\s+' +                                        # DCL Time-Stamp
    r'SAT(\w{3})' + r'(\d{4}),' + INTEGER + r',' +                  # Measurement type and serial#
    FLOAT + r',' + FLOAT + r',' + FLOAT + r',' +                    # hours, nitrate and nitrogen
    FLOAT + r',' + FLOAT + r',' + FLOAT + r',' +                    # abs_254, abs_250 and bromide
    INTEGER + r',' + INTEGER + r',' + INTEGER + r',' +              # average, dark and integration
    r'(([+-]?[0-9]+,){256})' +                                      # channel measurements
    FLOAT + r',' + FLOAT + r',' + FLOAT + r',' + INTEGER + r',' +   # temp (internal, spec and lamp) and lamp time
    FLOAT + r',' + FLOAT + r',' + FLOAT + r',' + FLOAT + r',' +     # humidity, voltage (main, lamp and internal)
    INTEGER + r',' + FLOAT + r',' + FLOAT + r',' +                  # current, fit aux 1 and 2
    FLOAT + r',' + FLOAT + r',' + FLOAT +                           # fit base 1 and 2 and rmse
    r',,,,,' + INTEGER + NEWLINE                                    # empty fields and checksum
)
REGEX = re.compile(PATTERN, re.DOTALL)

_parameter_names_suna = [
        'date_time_string',
        'measurement_type',
        'serial_number',
        'date_string',
        'decimal_hours',
        'nitrate_concentration',
        'nitrogen_in_nitrate',
        'absorbance_254',
        'absorbance_250',
        'bromide_trace',
        'spectral_average',
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
    A Parser subclass that calls the Parser base class, adds the SUNA specific
    methods to parse the data, and extracts the SUNA data records from the DCL
    daily log files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_suna)

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
        # Use the date_time_string to calculate an epoch timestamp (seconds
        # since 1970-01-01)
        epts = dcl_to_epoch(match.group(1))
        self.data.time.append(epts)
        self.data.date_time_string.append(str(match.group(1)))

        # Assign the remaining SUNA data to the named parameters
        self.data.measurement_type.append(str(match.group(2)))
        self.data.serial_number.append(int(match.group(3)))
        self.data.date_string.append(str(match.group(4)))
        self.data.decimal_hours.append(float(match.group(5)))
        self.data.nitrate_concentration.append(float(match.group(6)))
        self.data.nitrogen_in_nitrate.append(float(match.group(7)))
        self.data.absorbance_254.append(float(match.group(8)))
        self.data.absorbance_250.append(float(match.group(9)))
        self.data.bromide_trace.append(float(match.group(10)))
        self.data.spectral_average.append(int(match.group(11)))
        self.data.dark_value.append(int(match.group(12)))
        self.data.integration_factor.append(int(match.group(13)))
        channels = [int(i) for i in match.group(14).split(',')[:-1]]
        self.data.channel_measurements.append(channels)
        self.data.temperature_internal.append(float(match.group(16)))
        self.data.temperature_spectrometer.append(float(match.group(17)))
        self.data.temperature_lamp.append(float(match.group(18)))
        self.data.lamp_on_time.append(int(match.group(19)))
        self.data.humidity.append(float(match.group(20)))
        self.data.voltage_main.append(float(match.group(21)))
        self.data.voltage_lamp.append(float(match.group(22)))
        self.data.voltage_internal.append(float(match.group(23)))
        self.data.main_current.append(int(match.group(24)))
        self.data.fit_auxiliary_1.append(float(match.group(25)))
        self.data.fit_auxiliary_2.append(float(match.group(26)))
        self.data.fit_base_1.append(float(match.group(27)))
        self.data.fit_base_2.append(float(match.group(28)))
        self.data.fit_rmse.append(float(match.group(29)))


def main(argv=None):
    # load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for the SUNA data
    suna = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    suna.load_ascii()
    suna.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(suna.data.toJSON())


if __name__ == '__main__':
    main()
