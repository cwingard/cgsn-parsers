#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_xeos
@file cgsn_parsers/parsers/parse_xeos.py
@author Christopher Wingard
@brief Parses the Xeos beacon data emailed to the shore server
Note that the format has changed for Rover-X and Apollo-X beacons.
"""
import json
import os
import pandas as pd
import re

from calendar import timegm

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon, FilePointer
from cgsn_parsers.parsers.common import inputs, FLOAT, INTEGER, NEWLINE

# Regex pattern for legacy Xeos beacon data (kilo, melo)
LEGACY_PATTERN = (
    r'MOMSN=' + INTEGER + r',\s(.+),\s' + INTEGER + r'\s-\sTransfer\s(.*),\s' +
    r'bytes=' + INTEGER + r',\sLat:\s' + FLOAT + r'\sLon:\s' + FLOAT + r'\sCEPradius:\s' + INTEGER +
    r',\s(\d{8}),P,(\s|\w+)\s*' + FLOAT + r'\s' + FLOAT + r'\s' + INTEGER + r'\s' +
    r'(?:(\d+[a-z]{1})\s([+-]?[0-9]+)\s([+-]?[0-9]+)|([+-]?[0-9]+))' + NEWLINE
)
LEGACY_REGEX = re.compile(LEGACY_PATTERN, re.DOTALL)

# Regex pattern for the Rover-X and Apollo-X Xeos beacon data
# Note: Lat, Lon and CEPRadius values optional (depending on Iridium setup)
X_POS_PATTERN = (
    r'MOMSN=' + INTEGER + r',\s(.+?),\s' + INTEGER + r'\s-\sTransfer\s(.*?),\s' +
    r'bytes=' + INTEGER + r',\s(Lat:\s' + FLOAT + r'\sLon:\s' + FLOAT + r')?\sCEPradius:\s' + INTEGER + '?,\s' +
    r'AG,\s' + FLOAT + r',\s' + FLOAT + r',\s' + INTEGER + r',\s' + INTEGER + r',\s' +
    FLOAT + r',\s' + FLOAT + r',\s' + FLOAT + r',\s' + INTEGER + r',\s' +
    INTEGER + r',\s' + FLOAT + r',\s' + FLOAT + r',\s' + INTEGER + r',\s' + 
    FLOAT + r'\s*' + NEWLINE
)
#X_POS_REGEX = re.compile(X_POS_PATTERN, re.DOTALL)
X_POS_REGEX = re.compile(X_POS_PATTERN) # Note: re.DOTALL breaks match with optional groups   Why?

# Set an error message string for use when testing the parser switch.
SWITCH_ERROR = 'The subsurface beacon switch must be set to either 0 (surface) or 1 (subsurface).'

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
        'subsurface_beacon',
        'latitude_xeos',
        'longitude_xeos',
        'distance_from_center',
        'time_in_circle',
        'signal_strength',
        'battery_voltage',
        # X beacon specific fields
        'loaded_voltage',
        'sched_timer',
        'altitude',
        'num_satellites',
        'bearing',
        'measurement_speed',
        'time_to_fix',
        'highest_hdop'
    ]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the Xeos SBD
    specific methods to parse the data, and extract the beacon location and
    watch circle status from the Xeos beacon email.
    """
    def __init__(self, infile, surface, last_read):
        # test the subsurface beacon flag to make sure it can be converted to an integer
        try:
            surface = int(surface)
        except ValueError:
            print(SWITCH_ERROR)

        # test the subsurface beacon flag to make sure it is set to either 0 or 1
        if surface in [0, 1]:
            self.initialize(infile, _parameter_names_xeos)
            self.surface = int(surface)
            self.last_read = last_read
        else:
            raise ValueError(SWITCH_ERROR)

    def parse_data(self):
        """
        Iterate through the record lines (defined via the regex expression
        above) in the data object, and parse the data into a pre-defined
        dictionary object created using the Bunch class.
        """
        for line in self.raw:
            match = LEGACY_REGEX.match(line)
            if match:
                self._build_legacy_parsed_values(match)
                continue

            match = X_POS_REGEX.match(line)
            if match:
                self._build_xpos_parsed_values(match)
                continue


    def _build_xpos_parsed_values(self, match):
        """
        Extract the data from the relevant regex groups and assign to elements
        of the data dictionary for the Rover-X and Apollo-X format lines.
        """

        # Unlike legacy, use xeos time for time field
        self.data.time.append(int(match.group(13)))

        # Assign the remaining Xeos beacon data to the named parameters
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

        # Presence of estimated Lat/Lon is optional
        if match.group(6) is not None:
            self.data.estimated_latitude.append(float(match.group(7)))
            self.data.estimated_longitude.append(float(match.group(8)))
        else:
            self.data.estimated_latitude.append(0.0)
            self.data.estimated_longitude.append(0.0)

        # Presence of CEPradius value is optional
        if match.group(9) is not None:
            self.data.cep_radius.append(int(match.group(9)))
        else:
            self.data.cep_radius.append(0)

        # X beacon message assignments
        self.data.battery_voltage.append(float(match.group(10)))
        self.data.loaded_voltage.append(float(match.group(11)))
        self.data.sched_timer.append(int(match.group(12)))
        self.data.date_time_xeos.append(int(match.group(13)))
        self.data.latitude_xeos.append(float(match.group(14)))
        self.data.longitude_xeos.append(float(match.group(15)))
        self.data.altitude.append(float(match.group(16)))
        self.data.signal_strength.append(int(match.group(17)))
        self.data.num_satellites.append( int(match.group(18)))
        self.data.bearing.append(float(match.group(19)))
        self.data.measurement_speed.append(float(match.group(20)))
        self.data.time_to_fix.append(int(match.group(21)))
        self.data.highest_hdop.append(float(match.group(22)))

        self.data.subsurface_beacon.append(self.surface)

        # Legacy fields unused in x format messages

        # Per discussion w/ C. Wingard; use sched_timer to flag watch circle alarm
        if match.group(12) == '5':
            self.data.watch_circle_status.append(2) # alarm
        else:
            self.data.watch_circle_status.append(0)

        self.data.distance_from_center.append(0)
        self.data.time_in_circle.append(0)
 

    def _build_legacy_parsed_values(self, match):
        """
        Extract the data from the relevant regex groups and assign to elements
        of the data dictionary.
        """
        # Use the date/time strings to calculate an epoch timestamp (seconds since 1970-01-01)
        email = pd.to_datetime(match.group(2), format='%a %b %d %H:%M:%S %Y', exact=False, utc=True)
        beacon = pd.to_datetime(str(email.year) + match.group(9), format='%Y%m%d%H%M%S', utc=True)
        epts = timegm(beacon.timetuple())
        self.data.time.append(epts)

        # Assign the remaining Xeos beacon data to the named parameters
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
        # use unixtime here for compatibility with -x data
        #self.data.date_time_xeos.append(int(match.group(9)))
        self.data.date_time_xeos.append(epts)

        # convert the watch circle status text to numeric values and append to the list
        mode = 'watch'
        if match.group(10) == ' ':
            self.data.watch_circle_status.append(0)
            mode = 'no watch'
        elif match.group(10) == 'OK':
            self.data.watch_circle_status.append(1)
        elif match.group(10) == 'ALARM':
            self.data.watch_circle_status.append(2)
        self.data.subsurface_beacon.append(self.surface)
        self.data.latitude_xeos.append(float(match.group(11)))
        self.data.longitude_xeos.append(float(match.group(12)))
        if mode == 'watch':
            # if we have a full match, then the beacon is in watch circle mode, and we have the distance from the
            # center, time in the circle, signal strength, and the battery voltage
            self.data.distance_from_center.append(int(match.group(13)))
            circle = pd.to_timedelta(int(match.group(14)[:-1]), match.group(14)[-1])
            self.data.time_in_circle.append(circle.total_seconds() / 60.0 / 60.0 / 24.0)  # time in the circle in days
            self.data.signal_strength.append(int(match.group(15)))
            self.data.battery_voltage.append(float(match.group(16)) / 100.0)
        else:
            # otherwise, the beacon is not in watch circle mode, and we only have the signal strength and the
            # battery voltage and will need to add dummy values for the distance from the center and time in the
            # circle
            self.data.distance_from_center.append(0)
            self.data.time_in_circle.append(0)
            self.data.signal_strength.append(int(match.group(13)))
            self.data.battery_voltage.append(float(match.group(17)) / 100.0)

        # x beacon data, unused on legacy beacons
        self.data.loaded_voltage.append(0.0)
        self.data.sched_timer.append(0)
        self.data.altitude.append(0.0)
        self.data.num_satellites.append(0)
        self.data.bearing.append(0.0)
        self.data.measurement_speed.append(0.0)
        self.data.time_to_fix.append(0)
        self.data.highest_hdop.append(0.0)


def main(argv=None):
    # load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)
    surface = args.switch

    # initialize the file position object
    position_file = os.path.join(os.path.dirname(outfile), 'xeos_sbd_log.file_pointer.txt')
    position = FilePointer(position_file, 0)
    if os.path.isfile(position_file):
        # we always want to use this file if it exists
        position.load_position()
    else:
        # Create one using 0 (start of the file) for the default position
        position.save_position()

    # initialize the Parser object for the Xeos beacon data
    xeos = Parser(infile, surface, position.last_read)

    # load the data into a buffered object and parse the data into a dictionary
    xeos.load_ascii()

    # if we have data, parse it into a dictionary object and write it out along with the
    # last read position in the file
    if xeos.raw:
        xeos.parse_data()

        # write the resulting Bunch object via the toJSON method to a JSON formatted data file (note,
        # no pretty-printing keeping things compact). first check if the file already exists, and if
        # so, append the new data to the existing file.
        if os.path.isfile(outfile):
            # load the existing data
            with open(outfile, 'r') as f:
                data = json.load(f)

            # append the new data to the existing data
            for k, v in xeos.data.items():
                data[k].extend(v)

            # write the updated data back to the file
            with open(outfile, 'w') as f:
                json.dump(data, f)
        else:
            with open(outfile, 'w') as f:
                f.write(xeos.data.toJSON())

        # save the stream position to a text file
        position.last_read = xeos.last_read
        position.save_position()
    else:
        print('No new data to parse.')


if __name__ == '__main__':
    main()
