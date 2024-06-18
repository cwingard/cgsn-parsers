#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_ifcb_hdr
@file cgsn_parsers/parsers/parse_ifcb_hdr.py
@author Paul Whelan
@brief Parses McLane IFCB ascii header data files produced by the IFCB instrument
"""
import os
import re
import pandas as pd
from calendar import timegm
from pathlib import Path

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import inputs, NEWLINE


# == Parser for IFCB .HDR file type ==
            
# Regex pattern for extracting datetime from filename
FNAME_DTIME_PATTERN = (
    r'\w(\d\d\d\d\d\d\d\dT\d\d\d\d\d\d)_' +
    r'.+' +
    NEWLINE
  )
FNAME_DTIME = re.compile(FNAME_DTIME_PATTERN, re.DOTALL)

# Regex pattern for a line with ADCFileFormat: {list of column names}'
COLS_PATTERN = (
    r'(ADCFileFormat):\s' +               # Name
    r'(.+)' +                             # Value
    NEWLINE
)
COLS_REGEX = re.compile(COLS_PATTERN, re.DOTALL)

# Store param names in dictionary with values of corresponding data type
_param_names_ifcb_hdr_dict = {
    'ADCFileFormat': 'trigger#, ADCtime, PMTA, PMTB, PMTC, PMTD, PeakA, PeakB, PeakC, PeakD, TimeOfFlight, GrabTimeStart, GrabTimeEnd, RoiX, RoiY, RoiWidth, RoiHeight, StartByte, ComparatorOut, StartPoint, SignalLength, Status, RunTime, InhibitTime',
    }

class HdrParser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds to parse the IFCB header file
    """
    def __init__(self, infile):
        self.initialize(infile, list(_param_names_ifcb_hdr_dict.keys()))

    def parse_data(self):
        """
        Get the time value from the file name, then...
        Search for the line containing the ADCFileFormat key. This contains
        the list of column names of data in the ADC file.
        """
        match = FNAME_DTIME.match(os.path.basename(self.infile))
        if match:
            for line in self.raw:
                match = COLS_REGEX.match(line)
                if match:
                    self._build_parsed_values(match)
                    break

    def _build_parsed_values(self, match):
        """
        Extract the data from the relevant regex groups and assign to elements
        of the data dictionary.
        """
        # Get name value pair, then match to known parameters for value typing
        var_name = match.group(1)
        str_value = match.group(2).rstrip('\n')

        if var_name in _param_names_ifcb_hdr_dict.keys():
            self.data[var_name].append(str_value)
        

# == Parser for IFCB .ADC file type ==
            
# Regex pattern for a line in an adc file (csv lines)
ADC_LINE_PATTERN = (
    r'(.+)' +                             # Value
    NEWLINE
)
ADC_REGEX = re.compile(ADC_LINE_PATTERN, re.DOTALL)


class AdcParser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class for IFCB .adc files
    """
    def __init__(self, infile, col_names):
        self.initialize(infile, col_names )
        del self.data['time']
        self.col_names = col_names  # keep ordered list of keys for matching adc line data

    def parse_data(self):
        """
        Iterate through the lines (defined via the regex expression
        above) in the data object. 
        Verify that that the count of csv fields matches count of col_names.
        Append each value to the dictionary of col_names in same order
        """
        
        for line in self.raw:
            match = ADC_REGEX.match(line)
            if match:
                self._build_parsed_values(match)

    def _build_parsed_values(self, match):
        """
        Extract the data from the relevant regex groups and assign to elements
        of the data dictionary.
        """
        body = match.group(1).rstrip('\n')
        col_values = body.split(',')
        if len(col_values) != len(self.data.keys()):
            print("ADC column count does not match header file column list count. Ignoring line")
        else:
            for i in range(0, len(col_values)):
                self.data[ self.col_names[i] ].append( col_values[i] )
                  

def main(argv=None):
    # load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for ifcb header
    # get the list of .adc file columns from it
    hdr_path = Path(infile).with_suffix(".hdr")
    ifcb_hdr = HdrParser( str(hdr_path) )
    ifcb_hdr.load_ascii()
    ifcb_hdr.parse_data()
    adc_cols = ifcb_hdr.data[ "ADCFileFormat" ][0].split(", ")

    # Parse the .ADC file values
    ifcb_adc = AdcParser(infile, adc_cols)
    ifcb_adc.load_ascii()
    ifcb_adc.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(ifcb_adc.data.toJSON())


if __name__ == '__main__':
    main()
