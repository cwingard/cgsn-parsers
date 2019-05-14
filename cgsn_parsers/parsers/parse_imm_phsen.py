#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_imm_phsen
@file cgsn_parsers/parsers/parse_imm_phsen.py
@author Christopher Wingard
@brief Parses PHSEN data logged by the custom built WHOI data loggers via Inductive Modem (IMM) communications.
"""
import os
import re

from calendar import timegm
from datetime import datetime
from pytz import timezone

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import inputs, NEWLINE

# Regex pattern for a line with the IMM record number followed by the "*" character, 4 unknown characters (2 for a 1
# byte hash of the unit serial number and calibration, and 2 for the length byte), and a '0A' (indicating a Type 10 data
# record), with the follow on characters for the remaining bytes through the checksum and carriage return.
sample = (
    r'Record\[(\d+)\]:\*([0-9A-F]{2})([0-9A-F]{2})(0A)'         # Unique ID, record length and record type
    r'([0-9A-F]{8})([0-9A-F]{4})([0-9A-F]{64})' +               # Time, thermistor, and set of 16 reference measurements
    r'([0-9A-F]{368})[0-9A-F]{4}' +                             # 23 sets of 4 light measurements
    r'([0-9A-F]{4})([0-9A-F]{4})([0-9A-F]{2})' + NEWLINE        # Battery voltage, thermistor and checksum
)
REGEX = re.compile(sample, re.DOTALL)

# setup a base timestamp to convert the SAMI time in seconds since 1904 to an epoch timestamp (seconds since 1970)
dt = datetime.strptime('1904-01-01', '%Y-%m-%d')
dt.replace(tzinfo=timezone('UTC'))
BASE = timegm(dt.timetuple())

_parameter_names_phsen = [
    'record_number',
    'unique_id',
    'record_length',
    'record_type',
    'record_time',
    'thermistor_start',
    'reference_measurements',
    'light_measurements',
    'voltage_battery',
    'thermistor_end'
]


class Parser(ParserCommon):
    """
    A Parser class, with methods to load, parse the data, and save to JSON.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_phsen)

    def load_imm(self):
        """
        Create a buffered data object by opening the data file and reading in the contents as a single string
        """
        with open(self.infile, 'r') as fid:
            self.raw = fid.read()

    def parse_data(self):
        """
        Iterate through the record markers (defined via the regex expression above) in the data object, and parse the
        data file into a pre-defined dictionary object created using the Bunch class.
        """
        # find and parse the status data
        for match in re.finditer(REGEX, self.raw):
            if match:
                self._build_parsed_values(match)

    def _build_parsed_values(self, match):
        """
        Extract the data from the relevant regex groups and assign to elements of the data dictionary.
        """
        # assign the values
        self.data.record_number.append(int(match.group(1)))
        self.data.unique_id.append(int(match.group(2), 16))
        self.data.record_length.append(int(match.group(3), 16))
        self.data.record_type.append(int(match.group(4), 16))
        self.data.record_time.append(int(match.group(5), 16))
        self.data.thermistor_start.append(int(match.group(6), 16))

        # break the reference and light measurements out into lists
        refer = re.findall('....', match.group(7))
        self.data.reference_measurements.append([int(i, 16) for i in refer])
        light = re.findall('....', match.group(8))
        self.data.light_measurements.append([int(i, 16) for i in light])

        # assign remaining values
        self.data.voltage_battery.append(int(match.group(9), 16))
        self.data.thermistor_end.append(int(match.group(10), 16))

        # set the time to seconds since 1970-01-01
        self.data.time.append(int(match.group(5), 16) + BASE)


def main(argv=None):
    # load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for phsen
    phsen = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    phsen.load_imm()
    phsen.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(phsen.data.toJSON())


if __name__ == '__main__':
    main()
