#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_syslog_fb250
@file cgsn_parsers/parsers/parse_syslog_fb250.py
@author Christopher Wingard
@brief Parses the Sailor Fleet Broadband 250 data transfer statistics logged in the syslog files by the 
    custom built WHOI data loggers.
"""
import os
import re

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLOAT, INTEGER, NEWLINE

# Regex pattern for a summary FB250 log entry in the syslog
PATTERN = (
    DCL_TIMESTAMP + r'\s+DAT\sC_FB250\s+' +
    r'(\d{4}/\d{2}/\d{2}\s\d{2}:\d{2}:\d{2})\s+' +
    r'(UP|DOWN)\s+' + FLOAT + r'\s+' + INTEGER + r'\s+' + FLOAT + r'\s+' + FLOAT + r'\s+' +
    r'(\d{2}/\d{2}/\d{2}\s\d{2}:\d{2}:\d{2})\s+' + INTEGER + r'\s+' +
    r'dev\sfb(\d)\s+dur\s+' + INTEGER + r'\s+' +
    r'l_att\s+' + INTEGER + r'\s+' +
    r'l_stime\s+' + INTEGER + r'\s+' +
    r'l_stime\s+' + FLOAT + r'\s+' +
    r'l_etime\s+' + FLOAT + r'\s+' +
    r'tot\s+' + INTEGER + r'\s+' + INTEGER + r'\s+' + INTEGER + NEWLINE
)
REGEX = re.compile(PATTERN, re.DOTALL)

_parameter_names_fb250 = [
    'date_time_string',
    'link_state',
    'rssi',
    'temperature',
    'latitiude',
    'longitude',
    'fb250_device_id',
    'link_attempts',
    'elapsed_time'
]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the specific methods to parse the data, 
    and extracts the FB250 summary records from the daily CPM1 syslog files.
    """

    def __init__(self, infile):
        self.initialize(infile, _parameter_names_fb250)

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
        self.data.link_state.append(str(match.group(3)))
        self.data.rssi.append(float(match.group(4)))
        self.data.temperature.append(int(match.group(5)))
        self.data.latitiude.append(float(match.group(6)))
        self.data.longitude.append(float(match.group(7)))
        self.data.fb250_device_id.append(int(match.group(10)))
        self.data.link_attempts.append(int(match.group(12)))
        self.data.elapsed_time.append(int(match.group(16)))


if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for FB250 data
    fb250 = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    fb250.load_ascii()
    fb250.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(fb250.data.toJSON())
