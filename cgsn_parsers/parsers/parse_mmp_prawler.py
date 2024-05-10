#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_mmp_prawler
@file cgsn_parsers/parsers/parse_mmp_prawler.py
@author Paul Whelan
@brief Parses the Prawler MMP data files into a single JSON file. Files are mixed binary and ascii.
"""
import datetime
import numpy as np
import os
import re
from munch import Munch as Bunch
from struct import unpack, unpack_from

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon, inputs #, INTEGER, STRING, NEWLINE

# constants
ENG_DATA_SIZE = 34
SCI_DATA_SIZE = 31
STN_DATA_SIZE =  8

# byte representations of constants
STRING = b'(.+)'
INTEGER = b'([+-]?[0-9]+)'
NEWLINE = b'(?:\r\n|\n)?'
FLOAT = b'([+-]?\d+.\d+[Ee]?[+-]?\d*)'  # includes scientific notation

# File header for prawler data files
SUMMARY_PATTERN = (
    b'#UIMM Status' + NEWLINE +
    b'#7370_DateTime: ' + STRING + NEWLINE +
    b'#ID=' + INTEGER + NEWLINE +
    b'#SN=' + INTEGER + NEWLINE +
    b'#Volts=' + FLOAT + NEWLINE +
    b'#Records=' + INTEGER + NEWLINE +
    b'#Length=' + INTEGER + NEWLINE +
    b'#Events=' + INTEGER + NEWLINE
)
SUMMARY_MATCHER = re.compile(SUMMARY_PATTERN, re.DOTALL)


# Regex pattern for the start of a binary prawler data packet
REC_PATTERN = (
    b'Record\[(\d+)\]:@@@'
)
REC_REGEX = re.compile(REC_PATTERN, re.DOTALL)



class ParameterNames(object):
    """
    Parameter names for the three file types telemetered to shore from the McLane Prawler via the Shallow Water
    Profiler mooring STC system. 
    """

    def __init__(self):

        # File summary data
        #    1 line header = "#UIMM Status\r\n"
        #    1 line timestamp = "#7370_DateTime: yyyymmdd hhmmss\r\n"
        #    1 line ID = "ID=##\r\n"
        #    1 line serial number = "#SN=########\r\n"
        #    1 line voltage = "#Volts=##.##\r\n"
        #    1 line record count = "#Records=##\r\n"
        #    1 line length = "#Length=####\r\n"
        #    1 line events = "#Events=###\r\n"

        # Summary data parameters (prawler file header)
        self._summary_data = [
            'datetime',
            'ID',
            'serial_number',
            'voltage',
            'records',
            'length',
            'events'
        ]

        # Each engineering data message consists of the following:
        #    3 byte header = @@@
        #    2 bytes crc (not implemented)
        #    2 byte message length (after ID)
        #    1 byte ID ('G')
        #    2 byte depth (in meters)
        #    1 byte direction (1=climb, 2=fall, 3=park, 9=error)
        #    1 byte profile count
        #    1 byte sample rate
        #    1 byte inflection rate
        #    1 byte upper limit (meters)
        #    2 byte lower limit (meters)
        #    2 byte inflection point (meters)
        #    2 byte error timeout
        #    2 byte direction count
        #    2 byte error count
        #    2 byte vacuum level
        #    2 byte park time at lower limit (0=off)
        #    1 byte water detect (0=ok, 1=water) "ascii number"
        #    1 byte prawler mode (0=free fall, 1=station keeping) "ascii number"
        #    1 byte climb down (0=free fall, 1=climb down) "ascii number"
        #    1 byte calibration count (per day) "ascii number"
        #    3 bytes x00 x0D0A

        # Engineering data parameters
        self._eng_data = [
            'depth',
            'direction',
            'profile_count',
            'sample_rate',
            'inflection_rate',
            'upper_limit',
            'lower_limit',
            'inflection_point',
            'error_timeout',
            'direction_count',
            'error_count',
            'vacuum_level',
            'park_timer',
            'water_detect',
            'prawler_mode',
            'climb_down',
            'calibration'
        ]

        # Each science profile message consists of the following:
        #    3 byte header = @@@
        #    2 bytes crc (not implemented)
        #    2 byte message length (after ID)
        #    1 byte ID ('E')
        #    3 byte header = @@@
        #    4 bytes (undefined)
        #    n byte header line (ascii, ending in '\r\n')
        #    m profile data records, consisting of the following
        #        4 byte epoch time + ','
        #        4 byte depth + ','   (ascii hex digits), cvt to float, / by 100 to get depth (dB)
        #        4 byte temperature + ','  (ascii hex digits), cvt to float / by 1000 to get t (C)
        #        4 byte saliniby + ',' (ascii hex digits), cvt to float / by 1000 to get ?
        #        4 byte optode temp + ',' (ascii hex digits), cvt to float, / by 1000 to get t (C)
        #        4 byte dissolved o2 + '\r\n'
        #    2 byte '\r\n'

        # Science profile parameters
        self._sci_profile_data = [
            'epoch_time',
            'pressure',
            'temperature',
            'conductivity',
            'optode_temperature',
            'optode_dissolved_oxygen'
        ]

        # Each station list message consists of the following:
        #    3 byte header = @@@
        #    2 bytes crc (not implemented)
        #    2 byte message length (after ID)
        #    1 byte ID ('S')
        #    1 byte count of stations (n)
        #    n station records, consisting of the following:
        #        2 byte depth (m)
        #        2 byte count of samples taken at station (m)
        #        2 byte wait time before sampling (s)
        #        2 byte sampling rate (s)
        #        2 byte '\r\n'  (confirm this, as we don't have station examples)
        #    2 bytes '\r\n'

        # Station parameters
        self._stn_list_data = [
            'depth',
            'sample_num',
            'wait_time',
            'sample_rate'
        ]

    # Create the initial dictionary object from the parameter sets.
    def create_dict(self):
        """
        Create a Bunch class object to store the parameter names for the McClane Prawler used on the Shallow
        Water moorings, with the data organized hierarchically by the data type.
        """
        bunch = Bunch()
        bunch.summarydata = Bunch()
        bunch.engdata = Bunch()
        bunch.scidata = Bunch()
        bunch.stndata = Bunch()

        for name in self._summary_data:
            bunch.summarydata[name] = []

        for name in self._eng_data:
            bunch.engdata[name] = []

        for name in self._sci_profile_data:
            bunch.scidata[name] = []

        for name in self._stn_list_data:
            bunch.stndata[name] = []

        return bunch



class Parser(ParserCommon):
    """
    A Parser class, with methods to load, parse the data, and save to JSON the prawler data,
    separated into engineering data, science profile data and station list data 
    """
    def __init__(self, infile):
        # set the infile names
        self.infile = infile

        # initialize the data dictionary using the parameter names defined above
        data = ParameterNames()
        self.data = data.create_dict()

    def parse_prawler(self):
        """
        Iterate through the records looking for engineering data. Parse the
        data into the engdata structures
        """
        self.parse_summary()

        # find all the  data packets
        record_marker = [m.start() for m in REC_REGEX.finditer(self.raw)]
        #record_length = 0   # default record length set to 0, updated with first packet
        
        # if we have record packets, then parse them one-by-one
        while record_marker:
            # set the start point of the packet
            start = record_marker[0]

            # Scan past "Record[nnn]:" to type of records
            end = self.raw.find(b':', start)
            if end >= 0:
                start = end + 1

            rectype = self.raw[ start+7 ]

            # Engineering data ?
            if rectype == ord('G'):

                recstart = unpack_from( '<3s', self.raw, start )[0]
                while recstart == b'@@@':

                    self.unpack_engdata(start)
    
                    start = start + ENG_DATA_SIZE
                    recstart = unpack_from( '<3s', self.raw, start )[0]

            # Science profile data ?
            elif rectype == ord('E'):

                recstart = unpack_from( '<3s', self.raw, start )[0]

                if recstart != b'@@@':
                    continue

                # skip column list (ends in \r\n)
                here = start + 8
                eol = unpack_from( '2s', self.raw, here )[0]
                while eol != b'\x0d\x0a':
                    here = here + 1
                    eol = unpack_from( '2s', self.raw, here )[0]
                here = here + 2

                eol = unpack_from( '2s', self.raw, here )[0]
                while eol != b'\x0d\x0a':

                    self.unpack_scidata(here)

                    here = here + SCI_DATA_SIZE
                    eol = unpack_from( '2s', self.raw, here )[0]

            # Station list data ?
            elif rectype == ord('S'):

                recstart = unpack_from( '<3s', self.raw, start )[0]
                while recstart == b'@@@':

                    num_stations = unpack_from( '>B', self.raw, start + 8 )[0]

                    here = start + 9
                    for i in range( num_stations ):
                        self.unpack_stndata(here)
                        here = here + STN_DATA_SIZE
            else:
                #print("Unrecognized prawler data packet at " + str(start + 7))
                raise RuntimeError("Unrecognized prawler data packet at " + str(start + 7))

            record_marker.pop(0)

    def parse_summary(self):
        """
        Match the summary record at the start of the file (should be 1). Parse fields
        """
        match = SUMMARY_MATCHER.match(self.raw)
        if match:
            self.data.summarydata.datetime.append( match.group(1).rstrip().decode("utf-8") )
            self.data.summarydata.ID.append( match.group(2).decode("utf-8"))
            self.data.summarydata.serial_number.append( match.group(3).decode("utf-8"))
            self.data.summarydata.voltage.append( match.group(4).decode("utf-8"))
            self.data.summarydata.records.append( match.group(5).decode("utf-8"))
            self.data.summarydata.length.append( match.group(6).decode("utf-8"))
            self.data.summarydata.events.append( match.group(7).decode("utf-8"))

    def unpack_engdata(self, start):

        self.data.engdata.depth.append( unpack_from( '>H', self.raw, start+8 )[0])
        self.data.engdata.direction.append( unpack_from('>b', self.raw, start+10 )[0] )
        self.data.engdata.profile_count.append( unpack_from('>b', self.raw, start+11 )[0] )
        self.data.engdata.sample_rate.append( unpack_from('>b', self.raw, start+12 )[0] )
        self.data.engdata.inflection_rate.append( unpack_from('>b', self.raw, start+13 )[0] )
        self.data.engdata.upper_limit.append( unpack_from('>b', self.raw, start+14 )[0] )
        self.data.engdata.lower_limit.append( unpack_from('>H', self.raw, start+15 )[0] )
        self.data.engdata.inflection_point.append( unpack_from('>H', self.raw, start+17 )[0] )
        self.data.engdata.error_timeout.append( unpack_from('>H', self.raw, start+19 )[0] )
        self.data.engdata.direction_count.append( unpack_from('>H', self.raw, start+21 )[0] )
        self.data.engdata.error_count.append( unpack_from('>H', self.raw, start+23 )[0] )
        self.data.engdata.vacuum_level.append( unpack_from('>H', self.raw, start+25 )[0] )
        self.data.engdata.park_timer.append( unpack_from('>H', self.raw, start+27 )[0] )
        self.data.engdata.water_detect.append( unpack_from('c', self.raw, start+29 )[0].decode("utf-8") )
        self.data.engdata.prawler_mode.append( unpack_from('c', self.raw, start+30 )[0].decode("utf-8") )
        self.data.engdata.climb_down.append( unpack_from('c', self.raw, start+31 )[0].decode("utf-8") )
        self.data.engdata.calibration.append( unpack_from('c', self.raw, start+32 )[0].decode("utf-8") )

    def unpack_scidata(self, start):
        """
        Iterate through the record markers (defined via the regex expression above) in the data object, and parse the
        data file into a pre-defined dictionary object created using the Bunch class.
        """

        # Note: have seen science data packets terminate prematurely in files. When this
        # happens, ascii_hex_long_to_long throws an exception. So, make all the calls to that first.
        # If no exception is thrown, add the packet to the science data so we don't end up with partial
        # parsed packets of having to throw out the whole file.

        epoch_time = unpack_from('>L', self.raw, start )[0]
        pressure = float(self.ascii_hex_long_to_long( start + 5 )) / 100.0
        temp = float( self.ascii_hex_long_to_long( start + 10 )) / 1000.0
        cond = float( self.ascii_hex_long_to_long( start + 15 )) / 1000.0
        opt_temp = float( self.ascii_hex_long_to_long( start + 20 )) / 1000.0
        opt_o2 = float( self.ascii_hex_long_to_long( start + 25 )) / 1000.0

        self.data.scidata.epoch_time.append( epoch_time )
        self.data.scidata.pressure.append( pressure )
        self.data.scidata.temperature.append( temp )
        self.data.scidata.conductivity.append( cond )
        self.data.scidata.optode_temperature.append( opt_temp )
        self.data.scidata.optode_dissolved_oxygen.append( opt_o2 )

    def unpack_stndata(self, start):
        """
        Iterate through the record markers (defined via the regex expression above) in the data object, and parse the
        data file into a pre-defined dictionary object created using the Bunch class.
        """
        self.data.stndata.depth.append( unpack_from('>H', self.raw, start )[0])
        self.data.stndata.sample_num.append( unpack_from( '>H', self.raw, start + 2)[0])
        self.data.stndata.wait_time.append( unpack_from( '>H', self.raw, start + 4 )[0])
        self.data.stndata.sample_rate.append( unpack_from( '>H', self.raw, start + 6 )[0])

    def ascii_hex_long_to_long(self, start):
        """
        Converts a 4 char sequence of ascii hex characters into a long value in big endian order
        """
        # int conversion requires no comma trailing hex long
        long_str = unpack_from( '4s', self.raw, start )[0]
        long_out = -9999
        try:
            long_out = int( long_str, 16 )
        except:
            raise RuntimeError("Error converting data to long at " + str(start) + " value found: " + str(long_str))
        
        return long_out


def main(argv=None):

    # load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for the prawler data
    prawler = Parser(infile)

    # load the data into buffered objects and parse the data into dictionaries
    prawler.load_binary()
    try:
        prawler.parse_prawler()

    except RuntimeError as e:
        print(e)
        print("Parsing of input file " + infile + " terminated early")

    finally:
        # write the resulting Bunch object via the toJSON method to a JSON formatted data file
        with open(outfile, 'w') as f:
            f.write(prawler.data.toJSON())


if __name__ == '__main__':
    main()
