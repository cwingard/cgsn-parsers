#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_imm_adcp
@file cgsn_parsers/parsers/parse_imm_adcp.py
@author Christopher Wingard
@brief Parses ADCP data, in PD12 format, logged by the custom built WHOI data loggers via Inductive Modem (IMM)
    communications.
"""
import os
import re
import struct

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs

# Regex pattern for a PD12 data record logged via the IMM system on STCs and DCLs.
PATTERN = (
    b'Record\[([0-9]+)\]:([\x00-\xFF]+?)(?=\\r\\n)'
)
REGEX = re.compile(PATTERN, re.DOTALL)

# object from the struct class to read the binary portion of the data
PD12 = struct.Struct('<2HI3BH6BH3hi3B')
VEL = struct.Struct('<4h')

# assign parameter names
_parameter_names_pd12 = [
    'imm_record_number',
    'ensemble_number',
    'unit_id',
    'firmware_version',
    'firmware_revision',
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
    A Parser subclass that calls the ParserCommon base class, adds the ADCP PD12 specific methods to parse the data,
    and extracts the ADCP data records from the IMM log files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_pd12)

    def parse_data(self):
        """
        Iterate through the record lines (defined via the regex expression above) in the data object, and parse the
        data into a pre-defined dictionary object created using the Bunch class.
        """
        for match in REGEX.findall(self.raw):
            try:
                self._build_parsed_values(match)
            except ValueError as e:
                print(e)
                continue

    def _build_parsed_values(self, match):
        """
        Extract the data from the relevant regex groups and assign to elements of the data dictionary.
        """
        # parse the binary data packet -- part 1 of 2
        (packet_id, length, ensemble_number, unit_id, firmware_version,
         firmware_revision, year, month, day, hour, minute, second, csecond,
         heading, pitch, roll, temperature, pressure, _, start_bin, bins) = PD12.unpack(match[1][:34])

        # Do we have a valid packet?
        if packet_id != struct.unpack('<H', b'\x6E\x7F')[0]:
            raise ValueError("Packet ID mismatch, excluding packet from IMM record %d" % int(match[0]))

        # Calculate the checksum and test if we have a good packet
        total = 0
        for i in range(0, length):
            total += match[1][i]

        checksum = total & 65535    # bitwise and with 65535
        if checksum != struct.unpack("<H", match[1][-2:])[0]:
            raise ValueError("Checksum mismatch, excluding packet from IMM record %d" % int(match[0]))

        # construct date/time string
        dt_str = ("%4d/%02d/%02d %02d:%02d:%05.3f" % (year, month, day, hour, minute, (second + (csecond / 100))))
        epts = dcl_to_epoch(dt_str)     # convert to epoch time (seconds since 1970-01-01)
        self.data.time.append(epts)

        # record the IMM record number
        self.data.imm_record_number.append(int(match[0]))

        # assign the parameters
        self.data.ensemble_number.append(ensemble_number)
        self.data.unit_id.append(unit_id)
        self.data.firmware_version.append(firmware_version)
        self.data.firmware_revision.append(firmware_revision)
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
        self.data.pressure.append(pressure)
        self.data.start_bin.append(start_bin)
        self.data.bins.append(bins)

        # parse the binary data packet -- part 2 of 2
        chunk = match[1][34:]       # velocity bins
        n = len(chunk) // 2 // 4    # determine number of velocity bins
        offset = 0

        # create the empty lists for the velocity data
        east = []
        north = []
        vertical = []
        error = []
        for i in range(0, n):
            (a, b, c, d) = VEL.unpack(chunk[offset: offset + 8])
            east.append(a)
            north.append(b)
            vertical.append(c)
            error.append(d)
            offset += 8

        # assign the parameters
        self.data.eastward_velocity.append(east)
        self.data.northward_velocity.append(north)
        self.data.vertical_velocity.append(vertical)
        self.data.error_velocity.append(error)


def main(argv=None):
    # load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object
    adcp = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    adcp.load_binary()
    adcp.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(adcp.data.toJSON())


if __name__ == '__main__':
    main()
