#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_xeos
@file cgsn_parsers/parsers/parse_xeos.py
@author Christopher Wingard
@brief Parses the Xeos beacon data emailed to the shore server
"""
import os
import re

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon, FilePointer
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLOAT, INTEGER, STRING, NEWLINE

# Regex pattern for the power system records
# MOMSN=2377, Sun Oct  1 22:44:31 2023, 00 - Transfer OK, bytes=105, Lat: 46.21172 Lon: -123.81950 CEPradius: 9, 10012320,P,OK 46.18885 -123.85899 4 40m 44 1875
PATTERN = (
    r'MOMSN=' + INTEGER + r',\s(.+),\s' + INTEGER + r'\s-\sTransfer\s(.*),\s' +
    r'bytes=' + INTEGER + r',\sLat:\s' + FLOAT + r'\sLon:\s' + FLOAT + r'\sCEPradius:\s' + INTEGER +
    r',\s(\d{8}),P,(\w*)\s' + FLOAT + r'\s' + FLOAT + r'\s' + INTEGER + r'\s(\d+\w)\s' +
    INTEGER + r'\s' + INTEGER + NEWLINE
)
REGEX = re.compile(PATTERN, re.DOTALL)

_parameter_names_xeos = [
        'momsn',
        'date_time_email',
        'status_code',
        'transfer_status',
        'transfer_bytes',
        'estimated_latitude',
        'estimated_longitude',
        'cep_radius',
        'date_time_xeos',
        'watch_circle_status',
        'latitude',
        'longitude'
        'distance_from_center',
        'time_in_circle',
        'signal_strength',
        'battery_voltage'
    ]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the GPS specific
    methods to parse the data, and extracts the GPS data records from the DCL
    daily log files.
    """
    def __init__(self, infile, last_read):
        self.initialize(infile, _parameter_names_xeos)
        self.last_read = last_read

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
        epts = dcl_to_epoch(match.group(2))
        self.data.time.append(epts)
        self.data.date_time_string.append(str(match.group(1)))

        # Assign the remaining Xeos beacon data to the named parameters
        'momsn',
        'date_time_email',
        'status_code',
        'transfer_status',
        'transfer_bytes',
        'estimated_latitude',
        'estimated_longitude',
        'cep_radius',
        'date_time_xeos',
        'watch_circle_status',
        'latitude',
        'longitude'
        'distance_from_center',
        'time_in_circle',
        'signal_strength',
        'battery_voltage'
        self.data.momsn.append(int(match.group(1)))
        self.data.date_time_email.append(str(match.group(2)))
        self.data.status_code.append(int(match.group(3)))
        if match.group(4) == 'OK':
            # if the transfer was OK, and the fix isn't marked as bad, then append a 1 to the list
            self.data.transfer_status.append(1)
        else:
            # otherwise, append a 0 to the list
            self.data.transfer_status.append(0)
        self.data.transfer_bytes.append(int(match.group(5)))
        self.data.estimated_latitude.append(float(match.group(6)))
        self.data.estimated_longitude.append(float(match.group(7)))
        self.data.cep_radius.append(int(match.group(8)))
        self.data.date_time_xeos.append(str(match.group(9)))
        self.data.watch_circle_status.append(str(match.group(10)))
        self.data.latitude.append(float(match.group(11)))
        self.data.longitude.append(float(match.group(12)))
        self.data.distance_from_center.append(int(match.group(13)))
        self.data.time_in_circle.append(str(match.group(14)))
        self.data.signal_strength.append(int(match.group(15)))
        self.data.battery_voltage.append(float(match.group(16))) / 100.0

def main(argv=None):
    # load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the file position object
    position_file = os.path.join(os.path.dirname(infile), 'xeos_sbd_log.file_pointer.txt')
    position = FilePointer(position_file, 0)
    if os.path.isfile(position_file):
        # we always want to use this file if it exists
        position.load_position()
    else:
        # Create one using 0 (start of the file) for the default position
        position.save_position()

    # initialize the Parser object for the Xeos beacon data
    xeos = Parser(infile, position.last_read)

    # load the data into a buffered object and parse the data into a dictionary
    xeos.load_ascii()

    # if we have data, parse it into a dictionary object and write it out along with the
    # last read position in the file
    if xeos.raw:
        xeos.parse_data()

        # write the resulting Bunch object via the toJSON method to a JSON
        # formatted data file (note, no pretty-printing keeping things compact)
        with open(outfile, 'w') as f:
            f.write(xeos.data.toJSON())

        # save the stream position to a text file
        position.save_position(xeos.last_read)
    else:
        print('No new data to parse.')


if __name__ == '__main__':
    main()
