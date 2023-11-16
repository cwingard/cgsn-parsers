#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_rbrq3
@file cgsn_parsers/parsers/parse_rbrq3.py
@author Paul Whelan
@brief Parses RBR Presf Quartz3 data logged by the custom built WHOI data loggers.
"""
import os
import re

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLOAT,  NEWLINE

# Regex pattern for a line with the active column list

COLS_PATTERN = (
    r'(\[\w*:\w*\]:)' +                # DCL logger ID
    r'# Active channels: ' +           # Line prefix
    r'(.+)' +
    NEWLINE
)
COLS_REGEX = re.compile( COLS_PATTERN, re.DOTALL )

# Regex pattern for a line with a time stamp, unix time value and
# up to 7 channel data values. TBD: alter when coniguration known

DATA_PATTERN = (
    r'(\[\w*:\w*\]:)' +                # DCL logger ID
    DCL_TIMESTAMP + r',\s*' +              # PRESF Date and Time
    FLOAT + r',' +                         # PRESF Unix time (milliseconds since 1/1/1970)
    r'(.+)' +
#   FLOAT + r',' +                         # channel 1 data
#   FLOAT + r',' +                         # channel 2 data
#   FLOAT + r',' +                         # channel 3 data
#   FLOAT + r',' +                         # channel 4 data
#   FLOAT + r',' +                         # channel 5 data
#   FLOAT + r',' +                         # channel 6 data
#    FLOAT +                                # channel 7 data
    NEWLINE
)
DATA_REGEX = re.compile( DATA_PATTERN, re.DOTALL )

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
    A Parser subclass that calls the Parser base class, adds the rbr presf specific
    methods to parse the data, and extracts the rbr presf data records from the DCL
    daily log files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_presf)

        self.numChannels = 7   #default: all channels active
        self.activeChannels = _parameter_names_presf[ 2: ]

    def parse_data(self):
        """
        Iterate through the record lines (defined via the regex expression
        above) in the data object, and parse the data into a pre-defined
        dictionary object created using the Bunch class.
        """
        for line in self.raw:

            match = COLS_REGEX.match( line )
            if match:
                self.activeChannels = match.group(2).strip('\n').split('|')
                self.numChannels = len( self.activeChannels )

            else :
                match = DATA_REGEX.match(line)
                if match:
                    self._build_parsed_values(match)

    def _build_parsed_values(self, match):
        """
        Extract the data from the relevant regex groups and assign to elements
        of the data dictionary.
        """
        # Use the date_time_string to calculate an epoch timestamp (seconds since
        # 1970-01-01)
        epts = dcl_to_epoch(match.group(2))
        self.data.time.append(epts)
        self.data.date_time_string.append(str(match.group(2)))

        # Assign the unix date time in milliseconds next
        self.data.unix_date_time_ms.append(float(match.group(3)))

        # Remaining data correspond to active channels (default or previously read from log)
        channelDataList = match.group(4).strip('\n').split(',')
        for i in range(0, len(channelDataList)):
            self.data[ self.activeChannels[i] ].append( float( channelDataList[i] ))
        
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
