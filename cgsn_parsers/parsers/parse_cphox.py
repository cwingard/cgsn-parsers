#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_cphox
@file cgsn_parsers/parsers/parse_cphox.py
@author Christopher Wingard
@brief Parses the data from the Sea-Bird Scientific Deep SeapHOx (CPHOX) sensor.
"""
import os
import re

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLOAT, INTEGER, NEWLINE

PATTERN = (
    DCL_TIMESTAMP + r'\s*' +        # DCL Time-Stamp
    r'DSPHOX(\d{5}),' + r'\s*' +    # Serial number
    r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}),' + r'\s*' +  # Instrument clock
    INTEGER + r',\s*' +             # Sample Number
    INTEGER + r',\s*' +             # Error code
    FLOAT + r',\s*' +               # Temperature (degC)
    FLOAT + r',\s*' +               # pH
    FLOAT + r',\s*' +               # external reference electrode (volts)
    FLOAT + r',\s*' +               # pressure (dbar)
    FLOAT + r',\s*' +               # salinity (psu)
    FLOAT + r',\s*' +               # conductivity (mS/cm)
    FLOAT + r',\s*' +               # oxygen (mL/L)
    FLOAT + r',\s*' +               # internal relative humidity (%)
    FLOAT + NEWLINE                 # internal temperature (degC)
)
REGEX = re.compile(PATTERN, re.DOTALL)

_parameter_names_cphox = [
    'dcl_date_time_string',
    'serial_number',
    'sphox_date_time_string',
    'sample_number',
    'error_flag',
    'temperature',
    'seawater_ph',
    'external_reference',
    'pressure',
    'salinity',
    'conductivity',
    'oxygen_concentration',
    'internal_humidity',
    'internal_temperature'
]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the specific pH
    sensor methods to parse the data, and extracts the pH data records from
    the DCL daily log files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_cphox)

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

        # Add the remaining data to the data dictionary
        self.data.serial_number.append(str(match.group(2)))
        self.data.sphox_date_time_string.append(str(match.group(3)))
        self.data.sample_number.append(int(match.group(4)))
        self.data.error_flag.append(str(match.group(5)))
        self.data.temperature.append(float(match.group(6)))
        self.data.seawater_ph.append(float(match.group(7)))
        self.data.external_reference.append(float(match.group(8)))
        self.data.pressure.append(float(match.group(9)))
        self.data.salinity.append(float(match.group(10)))
        self.data.conductivity.append(float(match.group(11)))
        self.data.oxygen_concentration.append(float(match.group(12)))
        self.data.internal_humidity.append(float(match.group(13)))
        self.data.internal_temperature.append(float(match.group(14)))


def main(argv=None):
    # load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # load the data into a buffered object and parse the data into a dictionary
    cphox = Parser(infile)
    cphox.load_ascii()
    cphox.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON formatted data file (note, no pretty-printing
    # keeping things compact)
    with open(outfile, 'w') as f:
        f.write(cphox.data.toJSON())


if __name__ == '__main__':
    main()
