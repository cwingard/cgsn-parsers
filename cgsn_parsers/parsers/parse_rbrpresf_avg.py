#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_rbrpresf_avg
@file cgsn_parsers/parsers/parse_rbrpresf_avg.py
@author Paul Whelan
@brief Parses RBR Presf Quartz3 hourly averaged (tide) data logged by the dl_rbrpresf data logger
and subsequently post-processed by the rbr_presf_avg utility to compute hourly averages and
convert the output to ascii.
Note: The quartz3 supports configurable, active columns of data. It was therefore necessary
in the logger to query active columns and log the list of active columns. This parser looks
for that log entry and will replace the default list of all data columns with those that are
reported as active. Data in logged data lines is then mapped in order to those column names.
Note: output files from the parse_rbrpresf_avg parser contain are the same as those produced by
    the parse_rbrq3 parser from raw log files (the data values are just hourly averages of the
    same data). Therefore, these files can be processed by the proc_rbrpresf processor that
    handles raw presf data. No new processor was written for this data.
"""
import os
import re
from datetime import datetime, timezone, timedelta
from munch import Munch as Bunch
from struct import unpack, unpack_from

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs
from cgsn_parsers.parsers.common import FLOAT, INTEGER, NEWLINE

TIMESTAMP = r'(\d{4}/\d{2}/\d{2}\s\d{2}:\d{2}:\d{2})'

# Regex pattern for a line with the Active Column list

COLS_PATTERN = (
    r'(\[presf:\w+\]:)# Active channels: ([a-zA-Z0-9_|]+)' + NEWLINE
)
COLS_REGEX = re.compile(COLS_PATTERN, re.DOTALL)

# Regex pattern for data line: timestamp,unixtime[,float]+

#DATA_PATTERN = (
#    TIMESTAMP + r',' +
#    FLOAT + 
#    r'(?:),' + FLOAT + r'){1,}' + NEWLINE
#)
DATA_PATTERN = (
    TIMESTAMP + r',' +
    INTEGER + r',.+' + NEWLINE
)
DATA_REGEX = re.compile(DATA_PATTERN, re.DOTALL)

# Default list of reported data columns, in order.
# Can be overridden with log entry containing active columns

_parameter_names_presf = [
        'date_time_string',
        'unix_date_time_ms',
        'temperature_00',
        'pressure_00',
        'temperature_01',
        'seapressure_00',
        'depth_00',
        'period_00',
        'period_01'
    ]

class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the rbr quartz3 presf specific
    methods to parse the data, and extracts the rbr presf data records from the DCL
    daily log files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_presf)

        self.num_channels = 7   #default: all channels active
        self.active_channels = _parameter_names_presf[2:]

        # set the infile names
        self.infile = infile


    def parse_data(self):
        """
        Parse through the messages looking for data samples
        """

        # Capture the 1st instance of an active channels message to
        # update the list of channels to output

        for line in self.raw:
            channels_match = COLS_REGEX.match(line)
            if channels_match:
                self.update_channel_count(channels_match)
                break

        # Iterate through datestamped hourly average records for output

        for line in self.raw:
            data_match = DATA_REGEX.match(line)
            if data_match:

                self.data.date_time_string.append(data_match.group(1))
                self.data.unix_date_time_ms.append(data_match.group(2))
                self.data.time.append( int( data_match.group(2)) )

                data_vals = line.split(',')
                for i in range(0, self.num_channels):
                    self.data[self.active_channels[i]].append( float(data_vals[2+i].rstrip()) )


    def update_channel_count( self, channelMatch ):
        """
        Update the default active channel list and count from file
        """
        self.active_channels = channelMatch.group(2).split(r'|')
        self.num_channels = len( self.active_channels )

        
def main(argv=None):
    # load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for flort
    presf = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    presf.load_ascii()
    presf.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(presf.data.toJSON())

if __name__ == '__main__':
    main()
