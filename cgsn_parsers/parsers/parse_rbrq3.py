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

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLOAT,  NEWLINE

# Regex pattern for a line with the active column list

COLS_PATTERN = (
    DCL_TIMESTAMP + r' ' +             # DCL timestamp
    r'(\[\w*:\w*\]:)' +                # DCL logger ID
    r'# Active channels: ' +           # Line prefix
    r'(.+)' +
    NEWLINE
)
COLS_REGEX = re.compile( COLS_PATTERN, re.DOTALL )

# Regex pattern for a line with a time stamp, unix time value and
# up to 7 channel data values. 

DATA_PATTERN = (
    DCL_TIMESTAMP + r' ' +             # DCL timestamp
    r'(\[\w*:\w*\]:)' +                # DCL logger ID
    DCL_TIMESTAMP + r',\s*' +          # PRESF Date and Time
    FLOAT + r',' +                     # PRESF Unix time (milliseconds since 1/1/1970)
    r'(.+)' +
    NEWLINE
)
DATA_REGEX = re.compile( DATA_PATTERN, re.DOTALL )

# Default list of reported data columns, in order.
# Can be overridden with log entry containing active columns

_parameter_names_presf = [
        'dcl_date_time_string',
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
        self.active_channels = _parameter_names_presf[ 3: ]

    def parse_data(self):
        """
        Iterate through the record lines (defined via the regex expression
        above) in the data object, and parse the data into a pre-defined
        dictionary object created using the Bunch class.
        """
        for line in self.raw:

            match = COLS_REGEX.match( line )
            if match:
                self.active_channels = match.group(3).strip('\n').split('|')
                self.num_channels = len( self.active_channels )

            else :
                match = DATA_REGEX.match(line)
                if match:
                    self._build_parsed_values(match)

    def _build_parsed_values(self, match):
        """
        Extract the data from the relevant regex groups and assign to elements
        of the data dictionary.
        """

        # Assign the DCL date_time_string
        self.data.dcl_date_time_string.append(str(match.group(1)))
        
        # Use the instrument date_time_string to calculate an epoch timestamp
        # (seconds since 1970-01-01)
        epts = dcl_to_epoch(match.group(3))
        self.data.time.append(epts)
        self.data.date_time_string.append(str(match.group(3)))

        # Assign the instrument unix date time in milliseconds next
        self.data.unix_date_time_ms.append(float(match.group(4)))

        # Remaining data correspond to active channels (default or previously read from log)
        channel_data_list = match.group(5).strip('\n').split(',')
        for i in range(0, len(channel_data_list)):
            self.data[ self.active_channels[i] ].append( float( channel_data_list[i] ))
        
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

    # purge any channels for which no data was provided
    for ch in _parameter_names_presf :
        if len( presf.data[ ch ] ) == 0 :
            del presf.data[ ch ]

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(presf.data.toJSON())

if __name__ == '__main__':
    main()
