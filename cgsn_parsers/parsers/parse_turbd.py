#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_turbd
@file cgsn_parsers/parsers/parse_turbd.py
@author Paul Whelan (derived from parse_flort.py)
@brief Parses Seapoint turbidity data logged by an RBR Virtuoso logger..
"""
import os
import re

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLOAT, INTEGER, STRING, NEWLINE

# Regex pattern for a line with a DCL time stamp, possible DCL status value and
# the 12 following met data values.
PATTERN = (
    DCL_TIMESTAMP + r'\s+' +                   # DCL Time-Stamp
    r'([0-9]{4,4}\-[0-9]{2,2}\-[0-9]{2,2}\s+' + # TURBD Date and Time
    r'[0-9]{2,2}:[0-9]{2,2}:[0-9]{2,2}\.[0-9]{3,3}),' + r'\s+' +
    FLOAT   + r'\s+' +                         # raw turbidity measurement
    STRING  + r'\s+' +                         # optional units
    NEWLINE
)
REGEX = re.compile(PATTERN, re.DOTALL)

_parameter_names_turbd = [
        'dcl_date_time_string',
        'turbd_date_time_string',
        'raw_signal_turbidity',
        'turbd_units'
    ]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the flort specific
    methods to parse the data, and extracts the flort data records from the DCL
    daily log files.
    """
    def __init__( self, infile ):
        self.initialize( infile, _parameter_names_turbd )

    def parse_data(self):
        """
        Iterate through the record lines (defined via the regex expression
        above) in the data object, and parse the data into a pre-defined
        dictionary object created using the Bunch class.
        """
        for line in self.raw:
            match = REGEX.match( line )
            if match:
                self._build_parsed_values( match )

    def _build_parsed_values( self, match ):
        """
        Extract the data from the relevant regex groups and assign to elements
        of the data dictionary.
        """
        # Use the date_time_string to calculate an epoch timestamp (seconds since
        # 1970-01-01)
        epts = dcl_to_epoch( match.group( 1 ) )
        self.data.time.append( epts )
        self.data.dcl_date_time_string.append( str(match.group( 1 )) )

        # Assign the remaining turbidity data to the named parameters
        self.data.turbd_date_time_string.append( re.sub('\t', ' ', str(match.group( 2 ) )))
        self.data.raw_signal_turbidity.append( float( match.group( 3 )))
        self.data.turbd_units.append( match.group( 4 ))

def main(argv=None):
    # load the input arguments
    args = inputs( argv )
    infile = os.path.abspath( args.infile )
    outfile = os.path.abspath( args.outfile )

    # initialize the Parser object for flort
    turbd = Parser( infile )

    # load the data into a buffered object and parse the data into a dictionary
    turbd.load_ascii()
    turbd.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write( turbd.data.toJSON() )

if __name__ == '__main__':
    main()
