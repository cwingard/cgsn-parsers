#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_superv_cpm
@file cgsn_parsers/parsers/parse_superv_cpm.py
@author Christopher Wingard
@brief Parses the CPM or STC supervisor data emailed to the shore server via SBD messages
"""
import json
import os
import pandas as pd
import re

from calendar import timegm
from json.decoder import JSONDecodeError

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon, FilePointer
from cgsn_parsers.parsers.common import inputs, FLOAT, INTEGER, NEWLINE

# Regex pattern for the SBD beacon data (either from a CPM or STC)
CPM_PATTERN = (
    r'MOMSN=' + INTEGER + r',\s(.+),\s' + INTEGER + r'\s-\sTransfer\s(.*),\s' +
    r'bytes=' + INTEGER + r',\sLat:\s' + FLOAT + r'\sLon:\s' + FLOAT + r'\sCEPradius:\s' + INTEGER + r',\s' +
    r'mpic_cpm:\s+' + FLOAT + r'\s' + FLOAT + r'\s0.0\s0.0\s' + r'([0-9a-f]{8})\s' +
    r't\s' + FLOAT + r'\s' + FLOAT + r'\s' + r'h\s' + FLOAT + r'\s' + r'p\s' + FLOAT + r'\s' +
    r'0.0\s0.0\s0.0\sndata\sndata\sndata\spv\s0\swt\s0\sfc\s0\s' +  # suspect this was meant to be PSC data, just filler
    r'sbd\s' + INTEGER + r'\s' + INTEGER + r'\s' +
    r'gf\s([0-9a-f]{1})\s'
    r'ld\s([0-9a-f]{1})\s'
    r'hb\s([0-1]+)\s' + INTEGER + r'\s' + INTEGER + r'\s' +
    r'wake\s([0-9]{2})\s' +
    r'ir\s([0-1]+)\s' +
    r'fwwf\s([0-3]+)\s' +
    r'gps\s([0-1]+)\s' +
    r'pps\s([0-1]+)\s' +
    r'dcl\s([0-9a-f]{2})\s' +
    r'wtc\s' + FLOAT + r'\s' +
    r'wpc\s' + INTEGER + r'\s' +
    r'esw\s([0-3]+)\s' +
    r'dsl\s([0-1]+)\s' +
    r'[0-9a-f]{4}' + NEWLINE
)

STC_PATTERN = (
    r'MOMSN=' + INTEGER + r',\s(.+),\s' + INTEGER + r'\s-\sTransfer\s(.*),\s' +
    r'bytes=' + INTEGER + r',\sLat:\s' + FLOAT + r'\sLon:\s' + FLOAT + r'\sCEPradius:\s' + INTEGER + r',\s' +
    r'mpic_stc:\s' + FLOAT + r'\s' + FLOAT + r'\s' + r'([0-9a-f]{8})\s' +
    r't\s' + FLOAT + r'\s' + FLOAT + r'\s' + r'h\s' + FLOAT + r'\s' + r'p\s' + FLOAT + r'\s' +
    r'gf\s([0-9a-f]{1})\s' + r'ld\s([0-9a-f]{1})\s' + INTEGER + r'\s' + INTEGER + r'\s' +
    r'hb\s([0-1]+)\s' + INTEGER + r'\s' + INTEGER + r'\s' + r'wake\s([0-9]+)\s' +
    r'ir\s([+-]?[0-1]+)\s' + FLOAT + r'\s' + FLOAT + r'\s' + r'([0-2])\s' +
    r'fwwf\s([0-3]+)\s' + FLOAT + r'\s' + FLOAT + r'\s' + r'([0-3]+)\s' +
    r'gps\s([0-1]+)\s' + r'sbd\s([0-9]+)\s' + r'pps\s([0-1]+)\s' + r'imm\s([0-1]+)\s' +
    r'wtc\s' + FLOAT + r'\s' + r'wpc\s' + INTEGER + r'\s' +
    r'esw\s([0-3]+)\s' + r'dsl\s([0-1]+)\s' + r'([0-9a-f]{8})\s' +
    r'p1\s([0-1]+)\s' + FLOAT + r'\s' + FLOAT + r'\s([0-4]+)\s' +
    r'p2\s([0-1]+)\s' + FLOAT + r'\s' + FLOAT + r'\s([0-4]+)\s' +
    r'p3\s([0-1]+)\s' + FLOAT + r'\s' + FLOAT + r'\s([0-4]+)\s' +
    r'p5\s([0-1]+)\s' + FLOAT + r'\s' + FLOAT + r'\s([0-4]+)\s' +
    r'p7\s([0-1]+)\s' + FLOAT + r'\s' + FLOAT + r'\s([0-4]+)\s' +
    r'[0-9a-f]{4}' + NEWLINE
)

# Set an error message string for use when testing the parser switch.
SWITCH_ERROR = 'The supervisor type must be a string set as either cpm or stc (case insensitive).'


def _parameter_names_pwrsys(superv_type):
    parameter_names = [
        'momsn',
        'date_time_email',
        'status_code',
        'transfer_status',
        'transfer_bytes',
        'estimated_latitude',
        'estimated_longitude',
        'cep_radius',
        'main_voltage',
        'main_current',
        'temperature1',
        'temperature2',
        'humidity',
        'pressure',
    ]

    if superv_type == 'cpm':
        parameter_names.extend([
            'error_flags',
            'sbd_signal_strength',
            'sbd_message_pending',
            'ground_fault_enable',
            'leak_detect_enable',
            'heartbeat_enable',
            'heartbeat_delta',
            'heartbeat_threshold',
            'wake_code',
            'iridium_power_state',
            'fwwf_power_state',
            'gps_power_state',
            'pps_source',
            'dcl_power_state',
            'wake_time_count',
            'wake_power_count',
            'esw_power_state',
            'dsl_power_state'
        ])

    if superv_type == 'stc':
        parameter_names.extend([
            'error_flags1',
            'ground_fault_enable',
            'leak_detect_enable',
            'leak_detect_voltage1',
            'leak_detect_voltage2',
            'heartbeat_enable',
            'heartbeat_delta',
            'heartbeat_threshold',
            'wake_code',
            'iridium_power_state',
            'iridium_voltage',
            'iridium_current',
            'iridium_error_flag',
            'fwwf_power_state',
            'fwwf_voltage',
            'fwwf_current',
            'fwwf_power_flag',
            'gps_power_state',
            'sbd_signal_strength',
            'pps_source',
            'imm_power_state',
            'wake_time_count',
            'wake_power_count',
            'esw_power_state',
            'dsl_power_state',
            'error_flags2',
            'port1_power_state',
            'port1_voltage',
            'port1_current',
            'port1_error_flag',
            'port2_power_state',
            'port2_voltage',
            'port2_current',
            'port2_error_flag',
            'port3_power_state',
            'port3_voltage',
            'port3_current',
            'port3_error_flag',
            'port5_power_state',
            'port5_voltage',
            'port5_current',
            'port5_error_flag',
            'port7_power_state',
            'port7_voltage',
            'port7_current',
            'port7_error_flag'
        ])

    return parameter_names


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the specific
    methods to parse the SBD supervisor data and extract either the STC or CPM
    supervisor data from the SBD email.
    """
    def __init__(self, infile, superv_type, last_read):
        # test the supervisor type to make sure it is a string
        try:
            superv_type = superv_type.lower()
        except ValueError:
            print(SWITCH_ERROR)

        # test supervisor type to make sure it is one of our recognized configurations
        if superv_type in ['cpm', 'stc']:
            self.superv_type = superv_type
            self.initialize(infile, _parameter_names_pwrsys(self.superv_type))
            self.last_read = last_read
        else:
            raise ValueError(SWITCH_ERROR)

    def parse_data(self):
        """
        Iterate through the record lines (defined via the regex expression
        above) in the data object, and parse the data into a pre-defined
        dictionary object created using the Bunch class.
        """
        regex = None  # initialize the regex object
        if self.superv_type == 'cpm':
            regex = re.compile(CPM_PATTERN, re.DOTALL)

        if self.superv_type == 'stc':
            regex = re.compile(STC_PATTERN, re.DOTALL)

        for line in self.raw:
            match = regex.match(line)
            if match:
                self._build_parsed_values(match)

    def _build_parsed_values(self, match):
        """
        Extract the data from the relevant regex groups and assign to elements
        of the data dictionary.
        """
        # Use the date/time string from the email to calculate an epoch timestamp (seconds since 1970-01-01)
        email = pd.to_datetime(match.group(2), format='%a %b %d %H:%M:%S %Y', exact=False, utc=True)
        epts = timegm(email.timetuple())
        self.data.time.append(epts)

        # Assign the SBD email data to the named parameters
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

        # assign superv data shared by both the CPM and STC to the named parameters
        self.data.main_voltage.append(float(match.group(9)))
        self.data.main_current.append(float(match.group(10)))
        self.data.temperature1.append(float(match.group(12)))
        self.data.temperature2.append(float(match.group(13)))
        self.data.humidity.append(float(match.group(14)))
        self.data.pressure.append(float(match.group(15)))

        # assign CPM specific superv data to the named parameters
        if self.superv_type == 'cpm':
            self.data.error_flags.append(int(match.group(11), 16))
            self.data.sbd_signal_strength.append(int(match.group(16)))
            self.data.sbd_message_pending.append(int(match.group(17)))
            self.data.ground_fault_enable.append(int(match.group(18), 16))
            self.data.leak_detect_enable.append(int(match.group(19)))
            self.data.heartbeat_enable.append(int(match.group(20)))
            self.data.heartbeat_delta.append(int(match.group(21)))
            self.data.heartbeat_threshold.append(int(match.group(22)))
            self.data.wake_code.append(int(match.group(23), 16))
            self.data.iridium_power_state.append(int(match.group(24)))
            self.data.fwwf_power_state.append(int(match.group(25)))
            self.data.gps_power_state.append(int(match.group(26)))
            self.data.pps_source.append(int(match.group(27)))
            self.data.dcl_power_state.append(int(match.group(28), 16))
            self.data.wake_time_count.append(float(match.group(29)))
            self.data.wake_power_count.append(int(match.group(30)))
            self.data.esw_power_state.append(int(match.group(31)))
            self.data.dsl_power_state.append(int(match.group(32)))

        # assign the STC specific superv data to the named parameters
        if self.superv_type == 'stc':
            self.data.error_flags1.append(int(match.group(11), 16))
            self.data.ground_fault_enable.append(int(match.group(16), 16))
            self.data.leak_detect_enable.append(int(match.group(17), 16))
            self.data.leak_detect_voltage1.append(int(match.group(18)))
            self.data.leak_detect_voltage2.append(int(match.group(19)))
            self.data.heartbeat_enable.append(int(match.group(20)))
            self.data.heartbeat_delta.append(int(match.group(21)))
            self.data.heartbeat_threshold.append(int(match.group(22)))
            self.data.wake_code.append(int(match.group(23), 16))
            self.data.iridium_power_state.append(int(match.group(24)))
            self.data.iridium_voltage.append(float(match.group(25)))
            self.data.iridium_current.append(float(match.group(26)))
            self.data.iridium_error_flag.append(int(match.group(27)))
            self.data.fwwf_power_state.append(int(match.group(28)))
            self.data.fwwf_voltage.append(float(match.group(29)))
            self.data.fwwf_current.append(float(match.group(30)))
            self.data.fwwf_power_flag.append(int(match.group(31)))
            self.data.gps_power_state.append(int(match.group(32)))
            self.data.sbd_signal_strength.append(int(match.group(33)))
            self.data.pps_source.append(int(match.group(34)))
            self.data.imm_power_state.append(int(match.group(35)))
            self.data.wake_time_count.append(float(match.group(36)))
            self.data.wake_power_count.append(int(match.group(37)))
            self.data.esw_power_state.append(int(match.group(38)))
            self.data.dsl_power_state.append(int(match.group(39)))
            self.data.error_flags2.append(int(match.group(40), 16))

            self.data.port1_power_state.append(int(match.group(41)))
            self.data.port1_voltage.append(float(match.group(42)))
            self.data.port1_current.append(float(match.group(43)))
            self.data.port1_error_flag.append(int(match.group(44)))

            self.data.port2_power_state.append(int(match.group(45)))
            self.data.port2_voltage.append(float(match.group(46)))
            self.data.port2_current.append(float(match.group(47)))
            self.data.port2_error_flag.append(int(match.group(48)))

            self.data.port3_power_state.append(int(match.group(49)))
            self.data.port3_voltage.append(float(match.group(50)))
            self.data.port3_current.append(float(match.group(51)))
            self.data.port3_error_flag.append(int(match.group(52)))

            self.data.port5_power_state.append(int(match.group(53)))
            self.data.port5_voltage.append(float(match.group(54)))
            self.data.port5_current.append(float(match.group(55)))
            self.data.port5_error_flag.append(int(match.group(56)))

            self.data.port7_power_state.append(int(match.group(57)))
            self.data.port7_voltage.append(float(match.group(58)))
            self.data.port7_current.append(float(match.group(59)))
            self.data.port7_error_flag.append(int(match.group(60)))


def main(argv=None):
    # load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)
    superv_type = args.switch

    # initialize the file position object
    position_file = os.path.join(os.path.dirname(outfile), 'superv_sbd_log.file_pointer.txt')
    position = FilePointer(position_file, 0)
    if os.path.isfile(position_file):
        # we always want to use this file if it exists
        position.load_position()
    else:
        # Create one using 0 (start of the file) for the default position
        position.save_position()

    # initialize the Parser object for SBD supervisor data
    superv = Parser(infile, superv_type, position.last_read)

    # load the data into a buffered object
    superv.load_ascii()

    # if we have data, parse it into a dictionary object and write it out along with the
    # last read position in the file
    if superv.raw:
        # parse the data into a Bunch class dictionary object
        superv.parse_data()

        # write the resulting Bunch object via the toJSON method to a JSON formatted data file (note,
        # no pretty-printing keeping things compact). first check if the file already exists, and if
        # so, append the new data to the existing file.
        if os.path.isfile(outfile):
            # load the existing data
            with open(outfile, 'r') as f:
                try:
                    data = json.load(f)
                except JSONDecodeError:
                    data = {}
                    print('The file is empty or otherwise corrupted, creating a new one.')

            # append the new data to the existing data
            for k, v in superv.data.items():
                data[k].extend(v)

            # write the updated data back to the file
            with open(outfile, 'w') as f:
                json.dump(data, f)
        else:
            with open(outfile, 'w') as f:
                f.write(superv.data.toJSON())

        # save the stream position to a text file
        position.last_read = superv.last_read
        position.save_position()
    else:
        print('No new data to parse.')


if __name__ == '__main__':
    main()
