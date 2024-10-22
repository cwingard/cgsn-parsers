#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_imm_cphox
@file cgsn_parsers/parsers/parse_imm_cphox.py
@author Paul Whelan (copied from parse_testph.py)
@brief Parses the IMM output from the Deep SeapHOx V2 sensor.
"""
import os
import re
import pandas as pd
from calendar import timegm

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import inputs, DCL_TIMESTAMP, FLOAT, INTEGER, NEWLINE

# The difference in SeaPhox output from serial I/O to IMM is the lack of a DCL timestamp in the IMM data
SPHOX_REGEX = (
    r'(' + DCL_TIMESTAMP + r'\s+)?' +    # DCL Time-Stamp
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

def _parameter_names_seaphox():
    """
    Create the list of parameter names corresponding to the
    Sea-Bird Deep SeapHOx V2.
    :return parameter_names: list of parameter names
    """
    parameter_names = [
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

    return parameter_names


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the specific pH
    sensor methods to parse the data, and extracts the pH data records from
    the DCL daily log files.
    """
    def __init__(self, infile):

        self.initialize(infile, _parameter_names_seaphox())

    def parse_data(self):
        """
        Iterate through the record lines (defined via the regex expression above) in the data object, and parse the
        data into a pre-defined dictionary object created using the Bunch class.
        """
        regex = re.compile(SPHOX_REGEX, re.DOTALL)

        for line in self.raw:
            match = regex.match(line)
            if match:
                self._build_parsed_values(match)

    def _build_parsed_values(self, match):
        """
        Extract the data from the relevant regex groups and assign to elements of the data dictionary.
        """
        # Use the instrument date_time_string to calculate an epoch timestamp (seconds since
        # 1970-01-01)
        time_string = str(match.group(4))
        utc = pd.to_datetime(time_string, format='%Y-%m-%dT%H:%M:%S', utc=True)
        epts = timegm(utc.timetuple())
        self.data.time.append(epts)

        # Use the instrument date time for the record timestamp (non-imm uses DCL_TIMESTAMP)
        if match.group(1) is not None:
            self.data.dcl_date_time_string.append(str(match.group(2)))
        self.data.serial_number.append(str(match.group(3)))
        self.data.sphox_date_time_string.append(str(match.group(4)))
        self.data.sample_number.append(int(match.group(5)))
        self.data.error_flag.append(str(match.group(6)))
        self.data.temperature.append(float(match.group(7)))
        self.data.seawater_ph.append(float(match.group(8)))
        self.data.external_reference.append(float(match.group(9)))
        self.data.pressure.append(float(match.group(10)))
        self.data.salinity.append(float(match.group(11)))
        self.data.conductivity.append(float(match.group(12)))
        self.data.oxygen_concentration.append(float(match.group(13)))
        self.data.internal_humidity.append(float(match.group(14)))
        self.data.internal_temperature.append(float(match.group(15)))


def main(argv=None):
    # load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for the pH data
    try:
        seaphox = Parser(infile)
    except ValueError as e:
        print("Exception caught parsing seaphox data: " + str(e))
        return None

    # load the data into a buffered object and parse the data into a dictionary
    seaphox.load_ascii()
    seaphox.parse_data()

    if len(seaphox.data.dcl_date_time_string) == 0:
        seaphox.data.pop('dcl_date_time_string')

    # write the resulting Bunch object via the toJSON method to a JSON formatted data file (note, no pretty-printing
    # keeping things compact)
    with open(outfile, 'w') as f:
        f.write(seaphox.data.toJSON())


if __name__ == '__main__':
    main()
