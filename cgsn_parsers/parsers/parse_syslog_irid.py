#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_syslog_irid
@file cgsn_parsers/parsers/parse_syslog_irid.py
@author Christopher Wingard
@brief Parses the iridium summary data transfer statistic logged in the syslog files by the 
    custom built WHOI data loggers.
"""
import os
import re

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLOAT, INTEGER, NEWLINE

# Regex pattern for a summary Iridium log entry in the syslog
PATTERN = (
    DCL_TIMESTAMP + r'\s+DAT\sC_IRID\s+' +
    r'sent\s+' + INTEGER + r'\s+' +
    r'recv\s+' + INTEGER + r'\s+' +
    r'tx\s+' + INTEGER + r'\s+' +
    r'rx\s+' + INTEGER + r'\s+' +
    r'avg_tx_rate\s+' + FLOAT + r'\s+' +
    r'avg_rx_rate\s+' + FLOAT + r'\s+' +
    r'logintime\s+' + FLOAT + r'\s+' +
    r'ctime\s+' + FLOAT + NEWLINE
)
REGEX = re.compile(PATTERN, re.DOTALL)

_parameter_names_irid = [
    'date_time_string',
    'files_sent',
    'files_received',
    'bytes_sent',
    'bytes_received',
    'average_tx_rate',
    'average_rx_rate',
    'login_time',
    'connection_time',
]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the specific methods to parse the data, 
    and extracts the Iridium summary records from the daily CPM1 syslog files.
    """

    def __init__(self, infile):
        self.initialize(infile, _parameter_names_irid)

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
        self.data.files_sent.append(int(match.group(2)))
        self.data.files_received.append(int(match.group(3)))
        self.data.bytes_sent.append(int(match.group(4)))
        self.data.bytes_received.append(int(match.group(5)))
        self.data.average_tx_rate.append(float(match.group(6)))
        self.data.average_rx_rate.append(float(match.group(7)))
        self.data.login_time.append(float(match.group(8)))
        self.data.connection_time.append(float(match.group(9)))


if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for Iridium data
    irid = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    irid.load_ascii()
    irid.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(irid.data.toJSON())
