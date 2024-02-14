#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_swnd
@file cgsn_parsers/parsers/parse_swnd.py
@author Christopher Wingard
@brief Parses raw SWND module data logged by the custom-built WHOI data loggers.
"""
import os
import re

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLTNAN, NEWLINE

# Regex pattern for a line with a DCL time stamp, possible DCL status value and the 7 following SWND data values.
PATTERN = (
    DCL_TIMESTAMP + r'\s+' +   # DCL Time-Stamp
    r'(?:\[\w*:\w*\]:\s*)*' +  # DCL status string (usually not be present)
    FLTNAN + r'\s+' +          # WindObserver II U-axis wind speed (relative to the instrument)
    FLTNAN + r'\s+' +          # WindObserver II V-axis wind speed (relative to the instrument)
    FLTNAN + r'\s+' +          # WindObserver II speed of sound
    FLTNAN + r'\s+' +          # WindObserver II sonic temperature
    FLTNAN + r'\s+' +          # compass heading (aligned with the U-axis)
    FLTNAN + r'\s+' +          # compass x-axis tilt (aligned with the U-axis)
    FLTNAN + NEWLINE           # compass y-axis tilt (aligned with the V-axis)
)
REGEX = re.compile(PATTERN, re.DOTALL)

_parameter_names_swnd = [
    'dcl_date_time_string',
    'u_axis_wind_speed',
    'v_axis_wind_speed',
    'sonic_temperature',
    'speed_of_sound',
    'heading',
    'pitch',
    'roll'
]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the SWND specific
    methods to parse the data, and extracts the SWND data records from the DCL
    daily log files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_swnd)

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
        self.data.dcl_date_time_string.append(str(match.group(1)))

        # Assign the remaining SWND data to the named parameters
        self.data.u_axis_wind_speed.append(float(match.group(2)))
        self.data.v_axis_wind_speed.append(float(match.group(3)))
        self.data.speed_of_sound.append(float(match.group(4)))
        self.data.sonic_temperature.append(float(match.group(5)))
        self.data.heading.append(float(match.group(6)))
        self.data.pitch.append(float(match.group(7)))
        self.data.roll.append(float(match.group(8)))


def main(argv=None):
    """
    Main method for parsing the combined raw Gill WindObserver II ultrasonic
    anemometer and PNI TCM2.5 3-axis compass data recorded by the WHOI ASIMET
    Sonic Wind (SWND) module. Data is updated every 5 seconds and recorded in
    the DCL daily log files.

    @param argv: list of input arguments
    :param infile: the input file to be parsed
    :param outfile: the output file to be written
    :return: None
    """
    # load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for raw Gill WindObserver II (SWND) data
    swnd = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    swnd.load_ascii()
    swnd.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(swnd.data.toJSON())


if __name__ == '__main__':
    main()
