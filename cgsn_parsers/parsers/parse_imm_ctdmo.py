#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_imm_ctdmo
@file cgsn_parsers/parsers/parse_imm_ctdmo.py
@author Christopher Wingard
@brief Parses CTDMO data logged by the custom built WHOI data loggers via Inductive Modem (IMM) communications.
"""
import array
import os
import re

from binascii import unhexlify
from calendar import timegm
from datetime import datetime
from munch import Munch as Bunch
from pytz import timezone
from struct import unpack

# Import common utilities and base classes
from cgsn_parsers.parsers.common import INTEGER, FLOAT, NEWLINE, inputs

# Regex patterns to match the CTDMO status and data records.
status = (
    r'#SBE37-IM[\s\S]+SERIAL NO.\s+(\d{5})\s+(\d{2}\s+\w{3}\s+\d{4}\s+\d{2}:\d{2}:\d{2})' + NEWLINE +
    r'#vMain =\s+' + FLOAT + ', vLith =\s+' + FLOAT + NEWLINE +
    r'#samplenumber =\s+' + INTEGER + ', free =\s+' + INTEGER + NEWLINE +
    r'#.+' + NEWLINE +
    r'#sample interval =\s+\d+\s+seconds' + NEWLINE +
    r'#PressureRange =\s+' + INTEGER + NEWLINE
)
STATUS = re.compile(status, re.DOTALL)

data = (
    r'([0-9A-F]{5})([0-9A-F]{5})([0-9A-F]{4})([0-9A-F]{8})' + NEWLINE
)
DATA = re.compile(data, re.DOTALL)

# set up a base timestamp to convert the CTD time in seconds since 2000 to an epoch timestamp (seconds since 1970)
dt = datetime.strptime('2000-01-01', '%Y-%m-%d')
dt.replace(tzinfo=timezone('UTC'))
BASE = timegm(dt.timetuple())


class ParameterNames(object):
    """
    Parameter names for the two data record types in the IMM files.
    """
    def __init__(self):
        # CTD status data
        self._status = [
            'time',
            'serial_number',
            'date_time_string',
            'main_battery',
            'lithium_battery',
            'samples_recorded',
            'memory_free',
            'pressure_range'
        ]

        # CTD data record with raw oxygen (DOSTA), chlorophyll fluorescence and optical backscatter (FLORD)
        self._ctd = [
            'time',
            'raw_temperature',
            'raw_conductivity',
            'raw_pressure',
            'ctd_time'
        ]

    # Create the initial dictionary object for the status and ctd data records.
    def create_dict(self):
        """
        Create a Bunch class object to store the parameter names for the status and ctd data, with the data organized
        hierarchically by the data type.
        """
        bunch = Bunch()
        bunch.status = Bunch()
        bunch.ctd = Bunch()

        for name in self._status:
            bunch.status[name] = []

        for name in self._ctd:
            bunch.ctd[name] = []

        return bunch


class Parser(object):
    """
    A Parser class, with methods to load, parse the data, and save to JSON.
    """
    def __init__(self, infile):
        # set the infile names
        self.infile = infile

        # initialize the data dictionary using the parameter names defined above
        d = ParameterNames()
        self.data = d.create_dict()
        self.raw = None

    def load_imm(self):
        """
        Create a buffered data object by opening the data file and reading in the contents as a single string
        """
        with open(self.infile, 'r') as fid:
            self.raw = fid.read()

    def parse_status(self):
        """
        Iterate through the record markers (defined via the regex expression above) in the data object, and parse the
        data file into a pre-defined dictionary object created using the Bunch class.
        """
        # find and parse the status data
        for match in re.finditer(STATUS, self.raw):
            if match:
                self._build_parsed_status(match)

    def parse_ctd(self):
        """
        Iterate through the record markers (defined via the regex expression above) in the data object, and parse the
        data file into a pre-defined dictionary object created using the Bunch class.
        """
        # find and parse the ctd data
        for match in re.finditer(DATA, self.raw):
            if match:
                self._build_parsed_ctd(match)

    def _build_parsed_status(self, match):
        # assign the parameters
        self.data.status.serial_number.append(int(match.group(1)))
        self.data.status.date_time_string.append(str(match.group(2)))
        self.data.status.main_battery.append(float(match.group(3)))
        self.data.status.lithium_battery.append(float(match.group(4)))
        self.data.status.samples_recorded.append(int(match.group(5)))
        self.data.status.memory_free.append(int(match.group(6)))
        self.data.status.pressure_range.append(int(match.group(7)))

        # Use the date_time_string to calculate an epoch timestamp (seconds since 1970-01-01)
        dt = datetime.strptime(match.group(2), '%d %b %Y %H:%M:%S')
        dt.replace(tzinfo=timezone('UTC'))
        self.data.status.time = timegm(dt.timetuple())

    def _build_parsed_ctd(self, match):
        # assign the parameters
        self.data.ctd.raw_temperature.append(int(match.group(1), 16))
        self.data.ctd.raw_conductivity.append(int(match.group(2), 16))

        # pressure in reverse byte order
        dbar = bytearray(unhexlify(match.group(3)))
        self.data.ctd.raw_pressure.append(int.from_bytes(dbar, 'little'))

        # ctd time in reverse byte order
        ctime = bytearray(unhexlify(match.group(4)))
        ctd_time = int.from_bytes(ctime, 'little')  # seconds since 2000-01-01
        self.data.ctd.ctd_time.append(ctd_time)

        # Use the ctd time to calculate an epoch timestamp (seconds since 1970-01-01)
        self.data.ctd.time.append(ctd_time + BASE)


def main(argv=None):
    # load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object
    ctd = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    ctd.load_imm()
    ctd.parse_status()
    ctd.parse_ctd()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(ctd.data.toJSON())


if __name__ == '__main__':
    main()
