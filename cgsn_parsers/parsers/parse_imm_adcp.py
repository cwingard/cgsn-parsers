#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_imm_adcp
@file cgsn_parsers/parsers/parse_imm_adcp.py
@author Christopher Wingard
@brief Parses ADCP data logged by the custom built WHOI data loggers via Inductive Modem (IMM communications).
"""
import os
import re
import struct

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs

# Regex pattern for a PD12 data record logged by the IMM system on STCs and DCLs.
PATTERN = (
    b'Record\[([0-9]+)\]:([\x00-\xFF]+?)(?=\\r\\n)'
)
REGEX = re.compile(PATTERN, re.DOTALL)
for match in REGEX.findall(self.raw):
    print(len(match[1]))

# object from the struct class to read the binary portion of the data
PD12 = struct.Struct('<2HI3BH6BH3hi3B')
VEL = struct.Struct('<4h')

_parameter_names_pd12 = [
    'record_number',
    'ensemble_number',
    'unit_id',
    'cpu_firmware_version',
    'cpu_firmware_revision',
    'year',
    'month',
    'day',
    'hour',
    'minute',
    'second',
    'csecond',
    'heading',
    'pitch',
    'roll',
    'temperature',
    'pressure',
    'start_bin',
    'bins',
    'eastward_velocity',
    'northward_velocity',
    'vertical_velocity',
    'error_velocity'
]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the ParserCommon base class, adds the ADCP PD12 specific
    methods to parse the data, and extracts the ADCP data records from the IMM log files.
    """

    def __init__(self, infile):
        self.initialize(infile, _parameter_names_pd12)

    def parse_data(self):
        """
        Iterate through the record lines (defined via the regex expression
        above) in the data object, and parse the data into a pre-defined
        dictionary object created using the Bunch class.
        """
        for match in REGEX.findall(self.raw):
            self._build_parsed_values(match)

    def _build_parsed_values(self, match):
        """
        Extract the data from the relevant regex groups and assign to elements
        of the data dictionary.
        """
        # record the record number
        self.data.record_number.append(int(match[0]))

        # parse the binary data packet -- part 1 of 2
        (_, _, ensemble_number, unit_id, cpu_firmware_version,
         cpu_firmware_revision, year, month, day, hour,
         minute, second, csecond, heading, pitch,
         roll, temperature, pressure, _, start_bin, bins) = PD12.unpack(match[1][:34])

        # construct date/time string
        dt_str = ("%4d/%02d/%02d %02d:%02d:%05.3f" % (year, month, day, hour, minute, (second + (csecond / 100))))
        epts = dcl_to_epoch(dt_str)     # convert to epoch time (seconds since 1970-01-01
        self.data.time.append(epts)

        # assign 
        self.data.ensemble_number.append(ensemble_number)
        self.data.unit_id.append(unit_id)
        self.data.cpu_firmware_version.append(cpu_firmware_revision)
        self.data.cpu_firmware_revision.append(cpu_firmware_version)
        self.data.year.append(year)
        self.data.month.append(month)
        self.data.day.append(day)
        self.data.hour.append(hour)
        self.data.minute.append(minute)
        self.data.second.append(second)
        self.data.csecond.append(csecond)
        self.data.heading.append(heading * 0.01)
        self.data.pitch.append(pitch * 0.01)
        self.data.roll.append(roll * 0.01)
        self.data.temperature.append(temperature * 0.01)
        self.data.pressure.append(pressure * 0.01)
        self.data.start_bin.append(start_bin)
        self.data.bins.append(bins)

        # parse the binary data packet -- part 2 of 2
        chunk = match[1][34:]
        n = len(chunk) // 2 // 4
        offset = 0

        beam1 = []
        beam2 = []
        beam3 = []
        beam4 = []
        for i in range(1, n):
            (a, b, c, d) = VEL.unpack(chunk[offset: offset + 8])
            beam1.append(a)
            beam2.append(b)
            beam3.append(c)
            beam4.append(d)
            offset += 8

        self.data.eastward_velocity.append(beam1)
        self.data.northward_velocity.append(beam2)
        self.data.vertical_velocity.append(beam3)
        self.data.error_velocity.append(beam4)

if __name__ == '__main__':
    # load the input arguments
    args = inputs()
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for PCO2A
    adcp = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    adcp.load_binary()
    adcp.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(adcp.data.toJSON())
