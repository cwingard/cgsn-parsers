#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_mopak
@file cgsn_parsers/parsers/parse_mopak.py
@author Christopher Wingard
@brief Parses MOPAK data logged by the custom built WHOI data loggers.
1/16/2025  - ppw - added support for 3DM-GX5 protocol and data format
"""
import os
import re

from struct import Struct

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import logfilename_to_epoch, inputs, LOGFILENAME_TIMESTAMP

# supported types of 3DM-GX? sensors
MPTYPE_GX3 = 'gx3'
MPTYPE_GX5 = 'gx5'

#
# Type declarations for mopak 3dM-GX3 and earlier sensors
#

# Regex pattern for a binary MOPAK (Microstrain 3DM-GX3-25) data packet;
GX3_PATTERN = b'(\xCB)([\x00-\xff]{42})'
GX3_REGEX = re.compile(GX3_PATTERN, re.DOTALL)

# Struct class object for the MOPAK binary data byte streams
MOPAK_GX3 = Struct('>B9fIH')

_parameter_names_mopak_gx3 = [
        'acceleration_x',
        'acceleration_y',
        'acceleration_z',
        'angular_rate_x',
        'angular_rate_y',
        'angular_rate_z',
        'magnetometer_x',
        'magnetometer_y',
        'magnetometer_z',
        'timer'
    ]

#
# Type declarations for mopak 3dM-GX5 sensors
#

# Regex pattern for a binary MOPAK (Microstrain 3DM-GX3-25) data packet;
GX5_PATTERN = b'(ue)'
GX5_REGEX = re.compile(GX5_PATTERN, re.DOTALL)

GX5_HDR_LEN = 4                 # 'u' 'e' type len
GX5_CKSUM_LEN = 2               # 2 checksum bytes

GX5_PAYLD_TYP_ACC = 4           # acceleration data
GX5_PAYLD_TYP_RATE = 5          # rate data
GX5_PAYLD_TYP_MAG = 6           # mag field data
GX5_PAYLD_TYP_GPS = 18          # gps time data

_parameter_names_mopak_gx5 = [
        'acceleration_x',
        'acceleration_y',
        'acceleration_z',
        'angular_rate_x',
        'angular_rate_y',
        'angular_rate_z',
        'magnetometer_x',
        'magnetometer_y',
        'magnetometer_z',
        'gps_time_of_week',
        'gps_week',
        'gps_flags'
    ]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the mopak specific
    methods to parse the data, and extracts the mopak data records from the DCL
    daily log files.
    """
    def __init__(self, infile, mopak_type):

        self.mopak_type = mopak_type

        if mopak_type == MPTYPE_GX3:
            self.initialize(infile, _parameter_names_mopak_gx3)
        else:
            self.initialize(infile, _parameter_names_mopak_gx5)

    def parse_data(self):
        """
        Iterate through packets to parse the data into a pre-defined
        dictionary object created using the Bunch class.
        """

        if self.mopak_type == MPTYPE_GX3:
            self.parse_gx3_data()

        else:
            self.parse_gx5_data()


    def parse_gx3_data(self):
        """
        Iterate through packets to parse the data into a pre-defined
        dictionary object created using the Bunch class.
        """
        # determine epoch start time from characters in the log file name; the
        # date_time in this filename marks when the file was created...that's
        # actually kind of a problem for the inshore surface moorings, but it
        # can be corrected elsewhere.
        dt_regex = re.compile(LOGFILENAME_TIMESTAMP, re.DOTALL)
        match = dt_regex.search(self.infile)
        epts = logfilename_to_epoch(match.group(1))

        # the wake time of the unit (time before first packet is output)
        # is a function of the filtering width. we use a width of 100, to
        # output 10 Hz data. adding the wake time to the file start time,
        # should provide a better measure of when the data was collected.
        twake = 0.053 + (2. * 100. / 1000.)
        epts = epts + twake

        # find all the mopak data packets
        record_marker = [m.start() for m in GX3_REGEX.finditer(self.raw)]

        # if we have mopak records, then parse them one-by-one
        accxs, accys, acczs = [], [], []
        angxs, angys, angzs = [], [], []
        magxs, magys, magzs = [], [], []
        times, timers = [], []

        while record_marker:
            # set the start and stop points of the packet
            start = record_marker[0]
            stop = start + 43

            # create the packet and setup to grab the next one
            packet = self.raw[start:stop]
            record_marker.pop(0)

            # unpack the packet
            (_, accx, accy, accz, angx, angy, angz,
            magx, magy, magz, timer, check) = MOPAK_GX3.unpack(packet)

            # Check the size
            if len(packet) != 43:
                print("Incorrect packet size")
                print("MOPAK data packet failed to parse")
                continue

            # Check the checksum
            if check != self._calc_gx3_checksum(packet[:-2]):
                print("Checksum mismatch")
                continue

            times.append(epts + (timer / 62500.))
            accxs.append(accx)
            accys.append(accy)
            acczs.append(accz)
            angxs.append(angx)
            angys.append(angy)
            angzs.append(angz)
            magxs.append(magx)
            magys.append(magy)
            magzs.append(magz)
            timers.append(timer / 62500.)

        # assign the accumulated MOPAK data to the named parameters
        self.data.time = times
        self.data.acceleration_x = accxs
        self.data.acceleration_y = accys
        self.data.acceleration_z = acczs
        self.data.angular_rate_x = angxs
        self.data.angular_rate_y = angys
        self.data.angular_rate_z = angzs
        self.data.magnetometer_x = magxs
        self.data.magnetometer_y = magys
        self.data.magnetometer_z = magzs
        self.data.timer = timers

    @staticmethod
    def _calc_gx3_checksum(packet):
        # add integer representations of the 1-byte characters
        checksum = 0
        for byte in packet:
            checksum += byte

        # reduce checksum to 2 significant bytes
        checksum &= 65535
        return checksum


    def parse_gx5_data(self):
        """
        Iterate through packets to parse the data into a pre-defined
        dictionary object created using the Bunch class.
        """

        # GPS time data returned as "time of week" and "week number". Calculate
        # the epoch (seconds) for the start of the year so these gps time fields
        # can be translated to epoch (seconds).
        dt_regex = re.compile(LOGFILENAME_TIMESTAMP, re.DOTALL)
        match = dt_regex.search(self.infile)
        year_start = match.group(1)[0:4] + "0101_000000"     # yyyy + mmdd_hhmmss
        year_start_epoch = logfilename_to_epoch(year_start)

        # find all the 3DM-GX5 data packets
        record_marker = [m.start() for m in GX5_REGEX.finditer(self.raw)]

        # if we have GX5 records, each may contain some or all of the following:
        accxs, accys, acczs = [], [], []
        angxs, angys, angzs = [], [], []
        magxs, magys, magzs = [], [], []
        gps_times_of_week, gps_weeks, gps_flags = [], [], []
        times = []

        while record_marker:

            # set payload fields zero, as some cadences may vary
            # and not all will be present in each packet
            accx = 0.0
            accy = 0.0
            accz = 0.0
            angx = 0.0
            angy = 0.0
            angz = 0.0
            magx = 0.0
            magy = 0.0
            magz = 0.0
            tow = 0.0
            wk = 0
            flags = 0

            # set the start and stop points of the packet
            packet_start = record_marker[0]
            GX5_HDR_STR = Struct('>BBBB')
            hdr_bytes = GX5_HDR_STR.unpack(self.raw[ packet_start : packet_start+4])
            packet_len = hdr_bytes[3]
            packet_stop = packet_start + packet_len + GX5_HDR_LEN    # 4

            record_marker.pop(0)

            # Find and fill payload data in this packet (record)
            # (can be one or more of the payloads)

            # Struct class object for the 3DMGX3 packet payload contents
            GX5_PAYLD_HDR_STR = Struct('>BB')
            GX5_ACC_STR  = Struct('>BBfff')
            GX5_RATE_STR = Struct('>BBfff')
            GX5_MAG_STR  = Struct('>BBfff')
            GX5_GPS_STR  = Struct('>BBdHH')

            payload_start = packet_start + GX5_HDR_LEN

            while payload_start < packet_stop:

                #payload_bytes = self.raw[ payload_start:payload_start+2]
                payload_hdr = GX5_PAYLD_HDR_STR.unpack(self.raw[ payload_start : payload_start+2 ])
                payload_len = payload_hdr[0]
                payload_type = payload_hdr[1]

                payload = self.raw[ payload_start : payload_start + payload_len]

                if payload_type == GX5_PAYLD_TYP_ACC:
                    (_, _, accx, accy, accz) = GX5_ACC_STR.unpack(payload)
                elif payload_type == GX5_PAYLD_TYP_RATE:
                    (_, _, angx, angy, angz) = GX5_RATE_STR.unpack(payload)
                elif payload_type == GX5_PAYLD_TYP_MAG:
                    (_, _, magx, magy, magz) = GX5_MAG_STR.unpack(payload)
                elif payload_type == GX5_PAYLD_TYP_GPS:
                    (_, _, tow, wk, flags) = GX5_GPS_STR.unpack(payload)
                else:
                    print ("unsupported payload type ", payload_type )

                payload_start = payload_start + payload_len

            # append this packet's contents to output lists
            epoch_time = year_start_epoch + wk * (7*24*60*60) + tow
            times.append(epoch_time)
            accxs.append(accx)
            accys.append(accy)
            acczs.append(accz)
            angxs.append(angx)
            angys.append(angy)
            angzs.append(angz)
            magxs.append(magx)
            magys.append(magy)
            magzs.append(magz)
            gps_times_of_week.append(tow)
            gps_weeks.append(wk)
            gps_flags.append(flags)
            
        # assign the accumulated MOPAK data to the named parameters
        self.data.time = times
        self.data.acceleration_x = accxs
        self.data.acceleration_y = accys
        self.data.acceleration_z = acczs
        self.data.angular_rate_x = angxs
        self.data.angular_rate_y = angys
        self.data.angular_rate_z = angzs
        self.data.magnetometer_x = magxs
        self.data.magnetometer_y = magys
        self.data.magnetometer_z = magzs
        self.data.gps_time_of_week = gps_times_of_week
        self.data.gps_week = gps_weeks
        self.data.gps_flags = gps_flags


def main(argv=None):
    # load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)
    is_gx5 = args.switch

    # set mopak version from args ( default gx3 )
    mopak_type = MPTYPE_GX3
    if is_gx5 is not None:
        mopak_type = MPTYPE_GX5

    # initialize the Parser object for vel3d
    mopak = Parser(infile, mopak_type)

    # load the data into a buffered object and parse the data into dictionaries
    mopak.load_binary()
    mopak.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(mopak.data.toJSON())


if __name__ == '__main__':
    main()
