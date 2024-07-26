#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_rbrq3
@file cgsn_parsers/parsers/parse_rbrq3.py
@author Paul Whelan
@brief Parses RBR Presf Quartz3 data logged by the custom built WHOI data loggers.
Note: The quartz3 supports configurable, active columns of data. It was therefore necessary
in the logger to query active columns and log the list of active columns. This parser looks
for that log entry and will replace the default list of all data columns with those that are
reported as active. Data in logged data lines is then mapped in order to those column names.
"""
import os
import re
from datetime import datetime, timezone, timedelta
from munch import Munch as Bunch
from struct import unpack, unpack_from

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs

# Byte-based regex string constants (from common.py)
FLOAT = b'([+-]?\d+.\d+[Ee]?[+-]?\d*)'          # includes scientific notation
FLTINT = b'([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)'   # matches a float or an integer, includes scientific notation
FLTNAN = b'([+-]?\d+.\d+[Ee]?[+-]?\d*|NaN)'     # matches a float or a NaN, includes scientific notation
STRING = b'(\S+)'
INTEGER = b'([+-]?[0-9]+)'
NEWLINE = b'(?:\r\n|\n)?'

# Log entry prefix regex pattern

PREFIX_PATTERN = (
    b'\[presf:\w+\]'
)
PREFIX_REGEX = re.compile( PREFIX_PATTERN, re.DOTALL )

# Regex pattern for a line with the active column list

COLS_PATTERN = (
    b'(\[presf:\w+\]:)# Active channels: ([a-zA-Z0-9_|]+)' + NEWLINE
)
COLS_REGEX = re.compile( COLS_PATTERN, re.DOTALL )

# Pattern for binary data
# 8 byte timestamp, 4 byte float x n active columns (repeat) until [presf:*] encountered

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
        self.active_channels = _parameter_names_presf[ 2: ]

        # set the infile names
        self.infile = infile

        # initialize the data dictionary using the parameter names defined above
        #self.data = self.create_dict()

    def parse_data(self):
        """
        Parse through the messages looking for binary data samples
        """

        # The prefix string starts every log entry in the file.
        # Capture the 1st prefix for iterating the file by message

        match = PREFIX_REGEX.match( self.raw )
        self.prefix = match.group(0)

        # Binary data should follow some, but not all, "Active Channels" entries.
        # Find each "Active Channels" entry. It the succeeding log entry prefix is
        # further away than the length of the Active Channels entry then it is assumed
        # that binary data follows the Active Channels entry.

        # find all the  Active Channnel log entries
        channels = COLS_REGEX.finditer(self.raw)
        for channelMatch in channels:

            self.update_channel_count( channelMatch )

            # find succeeding log entry prefix
            (start,end) = channelMatch.span(0)
            next = self.raw.find( self.prefix, end )

            # no binary data follows, move on
            if next == end:
                continue

            # Process succeeding binary data
            self.parse_binary_data( end, next )


    def update_channel_count( self, channelMatch ):
        """
        Update the default active channel list and count from file
        """
        self.active_channels = channelMatch.group(2).split(b'|')
        self.num_channels = len( self.active_channels )

    def parse_binary_data( self, start, endPlusOne ):
        """
        Binary data consists of an arbitrary number of samples.
        Each sample consists of a timestamp (8 bytes) plus 1 float per active channel
        End of binary dat marked by prefix of next message ie: "[presf:DLOGP2]"
        """

        # Each binary chunk consists of a unix timestamp and one float per active channel

        at = start
        while at < endPlusOne:

            # Note: at/near end of file, last binary can get truncated
            # Try to detect and skip if possible
            if (endPlusOne - at) < ( 8 + 4 * self.num_channels ):
                break

            epoch_time = unpack_from('<q', self.raw, at )[0]
            self.data['unix_date_time_ms'].append( epoch_time )

            # Our processing infrastructure wants a time value (seconds sincs 1970)
            self.data['time'].append( epoch_time / 1000 )

            self.data['date_time_string'].append( self.to_date_time_string( epoch_time ))

            at = at + 8
            for ch in range( self.num_channels ):
                value = unpack_from( '<f', self.raw, at )[0]
                self.data[ self.active_channels[ ch ].decode("utf-8") ].append( value )
                at = at + 4

    def to_date_time_string( self, epoch_time_ms ):
        """
        Binary date is an 8 byte double in units of milliseconds since 1/1/1970
        Create a date time string from it.
        """
        msecs = float(epoch_time_ms)/1000 - float(epoch_time_ms/1000)
        secs = epoch_time_ms / 1000

        dt = datetime.fromtimestamp( secs, tz=timezone.utc )
        dt = dt + timedelta(milliseconds=msecs)

        dt_str = dt.strftime("%Y-%m-%d %H:%M:%S.%f")

        return dt_str

        
def main(argv=None):
    # load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for flort
    presf = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    presf.load_binary()
    presf.parse_data()

    # purge any channels for which no data was provided
    for ch in _parameter_names_presf :
        if len( presf.data[ ch ] ) == 0 :
            del presf.data[ ch ]
    #del presf.data[ 'time' ]

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(presf.data.toJSON())

if __name__ == '__main__':
    main()
