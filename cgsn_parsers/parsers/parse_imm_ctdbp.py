#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_imm_ctdbp
@file cgsn_parsers/parsers/parse_imm_ctdbp.py
@author Christopher Wingard
@brief Parses CTDBP data, with a DOSTA and FLORD attached as analog voltage channels, and logged by the
    custom built WHOI data loggers via Inductive Modem (IMM) communications.
"""
import os
import re

from munch import Munch as Bunch
from calendar import timegm
from datetime import datetime
from pytz import timezone

# Import common utilities and base classes
from cgsn_parsers.parsers.common import INTEGER, FLOAT, NEWLINE, inputs

# Regex patterns to match the CTDBP status and data records.
status = (
    r'#SBE 16plus-IM[\s\S]+SERIAL NO.\s+(\d{5})\s+(\d{2}\s+\w{3}\s+\d{4}\s+\d{2}:\d{2}:\d{2})' + NEWLINE +
    r'#vbatt =\s+' + FLOAT + ', vlith =\s+' + FLOAT + ',\s+' +
    r'ioper =\s+' + FLOAT + '\s+ma, ipump =\s+' + FLOAT + '\s+ma,\s+' + NEWLINE +
    r'#wait four seconds for biowiper to close: iext01 =\s+' + FLOAT + '\s+ma,\s+' +
    r'wait four seconds for biowiper to close: iext2345 =\s+' + FLOAT + '\s+ma' + NEWLINE +
    r'#status =[\s\S]+' + NEWLINE +
    r'#samples =\s+' + INTEGER + ', free =\s+' + INTEGER + NEWLINE
)
STATUS = re.compile(status, re.DOTALL)

data = (
    INTEGER + r',' + FLOAT + r',' + FLOAT + r',' + FLOAT + r',' +
    FLOAT + r',' + FLOAT + r',' +
    FLOAT + r',' + FLOAT + r',' +
    r'(\d{2}\w{3}\d{4}\d{2}:\d{2}:\d{2})' + NEWLINE
)
DATA = re.compile(data, re.DOTALL)


class ParameterNames(object):
    """
    Parameter names for the two data record types in the data files.
    """
    def __init__(self):
        # CTD status data
        self._status = [
            'time',
            'serial_number',
            'date_time_string',
            'main_battery',
            'lithium_battery',
            'main_current',
            'pump_current',
            'oxy_current',
            'eco_current',
            'samples_recorded',
            'memory_free'
        ]

        # CTD data record with raw oxygen (DOSTA), chlorophyll fluorescence and optical backscatter (FLORD)
        self._ctd = [
            'time',
            'serial_number',
            'temperature',
            'conductivity',
            'pressure',
            'raw_oxy_calphase',
            'raw_oxy_temp',
            'raw_chlorophyll',
            'raw_backscatter',
            'date_time_string'
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
        self.data.status.main_current.append(float(match.group(5)))
        self.data.status.pump_current.append(float(match.group(6)))
        self.data.status.oxy_current.append(float(match.group(7)))
        self.data.status.eco_current.append(float(match.group(8)))
        self.data.status.samples_recorded.append(int(match.group(9)))
        self.data.status.memory_free.append(int(match.group(10)))

        # Use the date_time_string to calculate an epoch timestamp (seconds since 1970-01-01)
        dt = datetime.strptime(match.group(2), '%d %b %Y %H:%M:%S')
        dt.replace(tzinfo=timezone('UTC'))
        self.data.status.time = timegm(dt.timetuple())

    def _build_parsed_ctd(self, match):
        # assign the parameters
        self.data.ctd.serial_number.append(int(match.group(1)))
        self.data.ctd.temperature.append(float(match.group(2)))
        self.data.ctd.conductivity.append(float(match.group(3)))
        self.data.ctd.pressure.append(float(match.group(4)))
        self.data.ctd.raw_oxy_calphase.append(float(match.group(5)))
        self.data.ctd.raw_oxy_temp.append(float(match.group(6)))
        self.data.ctd.raw_chlorophyll.append(float(match.group(7)))
        self.data.ctd.raw_backscatter.append(float(match.group(8)))
        self.data.ctd.date_time_string.append(str(match.group(9)))

        # Use the date_time_string to calculate an epoch timestamp (seconds since 1970-01-01)
        dt = datetime.strptime(match.group(9), '%d%b%Y%H:%M:%S')
        dt.replace(tzinfo=timezone('UTC'))
        self.data.ctd.time = timegm(dt.timetuple())

if __name__ == '__main__':
    # load the input arguments
    args = inputs()
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
