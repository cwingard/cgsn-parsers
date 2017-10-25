#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_syslog_rda
@file cgsn_parsers/parsers/parse_syslog_rda.py
@author Christopher Wingard
@brief Parses the RDA data logged in the syslog files by the custom built WHOI data loggers.
"""
import os
import re

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLOAT, NEWLINE

# Regex pattern for an RDA log entry in the syslog
PATTERN = (
    DCL_TIMESTAMP + r'\sDAT\sRDA[67]\srda:\s+' +
    FLOAT + r'\s+' + FLOAT + r'\s+' + r'([0-9a-f]{8})\s+' +
    r'gf\s+([0-9a-f]{1})\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' +
    r'type\s+([0-2]{1})' + r'\s+' +
    r'rda\s+([0-1]{1})' + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' +
    r'([0-9a-f]{3})' + NEWLINE
)
REGEX = re.compile(PATTERN, re.DOTALL)

_parameter_names_rda = [
    'date_time_string',
    'main_voltage',
    'main_current',
    'error_flags',
    'rda_type'
]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the DCL supervisor
    specific methods to parse the data, and extracts the METBK data records
    from the DCL daily log files.
    """

    def __init__(self, infile):
        self.initialize(infile, _parameter_names_rda)

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
        self.data.date_time_string.append(str(match.group(1)))

        # Assign the remaining data to the named parameters
        self.data.main_voltage.append(float(match.group(2)))
        self.data.main_current.append(float(match.group(3)))
        self.data.error_flags.append(int(match.group(4), 16))
        self.data.rda_type.append(int(match.group(10)))


def main(argv=None):
    # load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for RDA data
    rda = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    rda.load_ascii()
    rda.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(rda.data.toJSON())

if __name__ == '__main__':
    main()
