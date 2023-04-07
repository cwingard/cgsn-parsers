#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_pwrsys
@file cgsn_parsers/parsers/parse_pwrsys.py
@author Christopher Wingard
@brief Parses the Power System Controller and MPEA data logged by the custom built WHOI data loggers.
"""
import os
import re

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLOAT, FLTINT, NEWLINE

# Regex pattern for the Power System Controller (PSC) records
PATTERN_PSC = (
    DCL_TIMESTAMP + r'\s(?:PwrSys|DAT\sC_POWER_SYS)\spsc:' +
    FLOAT + r'\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'([0-9a-f]{4})\s([0-9a-f]{8})\s([0-9a-f]{8})\s' +
    r'pv1\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'pv2\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'pv3\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'pv4\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'wt1\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'wt2\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'fc1\s([0-1]{1})\s' + FLTINT + r'\s' + FLOAT + r'\s' +
    r'fc2\s([0-1]{1})\s' + FLTINT + r'\s' + FLOAT + r'\s' +
    r'bt1\s' + FLOAT + r'\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'bt2\s' + FLOAT + r'\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'bt3\s' + FLOAT + r'\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'bt4\s' + FLOAT + r'\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'ext\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'int\s' + FLOAT + r'\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'fcl\s' + FLOAT + r'\s' +
    r'swg\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'cvt\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'([0-1]{1})\s' + FLOAT + r'\s([0-9a-f]{8})\s' +
    r'(?:No_FC_Data\s)?' +
    r'([0-9a-f]{4})' + NEWLINE
)

# Regex pattern for the MPEA power system records
PATTERN_MPEA = (
    DCL_TIMESTAMP + r'\sMPEA\smpm:\s' +
    FLOAT + r'\s' + FLOAT + r'\s' +
    r'([0-9a-fA-F]{8})\s([0-9a-fA-F]{8})\s' +
    r'cv1\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'cv2\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'cv3\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'cv4\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'cv5\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'cv6\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'cv7\s([0-1]{1})\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'aux\s([0-1]{1})\s' + FLOAT + r'\s([0-1]{1})\s' +
    r'htl\s' + FLOAT + r'\s' + FLOAT + r'\s' + FLOAT + r'\s' + FLOAT + r'\s' + FLOAT + r'\s' + FLOAT + r'\s' +
    r'([0-9a-f]{4})' + NEWLINE
)

# Set an error message string for use when testing the parser switch.
SWITCH_ERROR = 'The PWRSYS type must be a string set as either psc or mpea (case insensitive).'


def _parameter_names_pwrsys(pwrsys_type):
    parameter_names = [
        'dcl_date_time_string',
        'main_voltage',
        'main_current'
    ]

    if pwrsys_type == 'mpea':
        parameter_names.extend([
            'error_flag1',
            'error_flag2',
            'cv1_state',
            'cv1_voltage',
            'cv1_current',
            'cv2_state',
            'cv2_voltage',
            'cv2_current',
            'cv3_state',
            'cv3_voltage',
            'cv3_current',
            'cv4_state',
            'cv4_voltage',
            'cv4_current',
            'cv5_state',
            'cv5_voltage',
            'cv5_current',
            'cv6_state',
            'cv6_voltage',
            'cv6_current',
            'cv7_state',
            'cv7_voltage',
            'cv7_current',
            'auxiliary_state',
            'auxiliary_voltage',
            'auxiliary_current',
            'hotel_5v_voltage',
            'hotel_5v_current',
            'temperature',
            'relative_humidity',
            'leak_detect',
            'internal_pressure'
        ])

    if pwrsys_type == 'psc':
        parameter_names.extend([
            'percent_charge',
            'override_flag',
            'error_flag1',
            'error_flag2',
            'solar_panel1_state',
            'solar_panel1_voltage',
            'solar_panel1_current',
            'solar_panel2_state',
            'solar_panel2_voltage',
            'solar_panel2_current',
            'solar_panel3_state',
            'solar_panel3_voltage',
            'solar_panel3_current',
            'solar_panel4_state',
            'solar_panel4_voltage',
            'solar_panel4_current',
            'wind_turbine1_state',
            'wind_turbine1_voltage',
            'wind_turbine1_current',
            'wind_turbine2_state',
            'wind_turbine2_voltage',
            'wind_turbine2_current',
            'fuel_cell1_state',
            'fuel_cell1_voltage',
            'fuel_cell1_current',
            'fuel_cell2_state',
            'fuel_cell2_voltage',
            'fuel_cell2_current',
            'battery_bank1_temperature',
            'battery_bank1_voltage',
            'battery_bank1_current',
            'battery_bank2_temperature',
            'battery_bank2_voltage',
            'battery_bank2_current',
            'battery_bank3_temperature',
            'battery_bank3_voltage',
            'battery_bank3_current',
            'battery_bank4_temperature',
            'battery_bank4_voltage',
            'battery_bank4_current',
            'external_voltage',
            'external_current',
            'internal_voltage',
            'internal_current',
            'internal_temperature',
            'fuel_cell_volume',
            'seawater_ground_state',
            'seawater_ground_positve',
            'seawater_ground_negative',
            'cvt_state',
            'cvt_voltage',
            'cvt_current',
            'cvt_interlock',
            'cvt_temperature',
            'error_flag3'])

    return parameter_names


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the PWRSYS specific
    methods to parse the data, and extracts the PWRSYS data records from the DCL
    daily log files.
    """
    def __init__(self, infile, pwrsys_type):
        # test the pwrsys_type to make sure it is a string
        try:
            pwrsys_type = pwrsys_type.lower()
        except ValueError as e:
            print(SWITCH_ERROR)

        # test pwrsys_type to make sure it is one of our recognized configurations
        if pwrsys_type in ['mpea','psc']:
            self.pwrsys_type = pwrsys_type
            self.initialize(infile, _parameter_names_pwrsys(self.pwrsys_type))
        else:
            raise ValueError(SWITCH_ERROR)

    def parse_data(self):
        """
        Iterate through the record lines (defined via the regex expression
        above) in the data object, and parse the data into a pre-defined
        dictionary object created using the Bunch class.
        """
        if self.pwrsys_type == 'mpea':
            regex = re.compile(PATTERN_MPEA, re.DOTALL)

        if self.pwrsys_type == 'psc':
            regex = re.compile(PATTERN_PSC, re.DOTALL)

        for line in self.raw:
            match = regex.match(line)
            if match:
                self._build_parsed_values(match)

    def _build_parsed_values(self, match):
        """
        Extract the data from the relevant regex groups and assign to elements
        of the data dictionary.
        """
        # Use the date_time_string to calculate an epoch timestamp (seconds since
        # 1970-01-01)
        epts = dcl_to_epoch(match.group(1))
        self.data.time.append(epts)
        self.data.dcl_date_time_string.append(str(match.group(1)))
        self.data.main_voltage.append(float(match.group(2)))
        self.data.main_current.append(float(match.group(3)))

        if self.pwrsys_type == 'mpea':
            # Assign the remaining MPEA data to the named parameters
            self.data.error_flag1.append(int(match.group(4), 16))
            self.data.error_flag2.append(int(match.group(5), 16))
            self.data.cv1_state.append(int(match.group(6)))
            self.data.cv1_voltage.append(float(match.group(7)))
            self.data.cv1_current.append(float(match.group(8)))
            self.data.cv2_state.append(int(match.group(9)))
            self.data.cv2_voltage.append(float(match.group(10)))
            self.data.cv2_current.append(float(match.group(11)))
            self.data.cv3_state.append(int(match.group(12)))
            self.data.cv3_voltage.append(float(match.group(13)))
            self.data.cv3_current.append(float(match.group(14)))
            self.data.cv4_state.append(int(match.group(15)))
            self.data.cv4_voltage.append(float(match.group(16)))
            self.data.cv4_current.append(float(match.group(17)))
            self.data.cv5_state.append(int(match.group(18)))
            self.data.cv5_voltage.append(float(match.group(19)))
            self.data.cv5_current.append(float(match.group(20)))
            self.data.cv6_state.append(int(match.group(21)))
            self.data.cv6_voltage.append(float(match.group(22)))
            self.data.cv6_current.append(float(match.group(23)))
            self.data.cv7_state.append(int(match.group(24)))
            self.data.cv7_voltage.append(float(match.group(25)))
            self.data.cv7_current.append(float(match.group(26)))
            self.data.auxiliary_state.append(int(match.group(27)))
            self.data.auxiliary_voltage.append(float(match.group(28)))
            self.data.auxiliary_current.append(float(match.group(29)))
            self.data.hotel_5v_voltage.append(float(match.group(30)))
            self.data.hotel_5v_current.append(float(match.group(31)))
            self.data.temperature.append(float(match.group(32)))
            self.data.relative_humidity.append(float(match.group(33)))
            self.data.leak_detect.append(float(match.group(34)))
            self.data.internal_pressure.append(float(match.group(35)))

        if self.pwrsys_type == 'psc':
            # Assign the remaining PSC data to the named parameters
            self.data.percent_charge.append(float(match.group(4)))
            self.data.override_flag.append(int(match.group(5), 16))
            self.data.error_flag1.append(int(match.group(6), 16))
            self.data.error_flag2.append(int(match.group(7), 16))
            self.data.solar_panel1_state.append(int(match.group(8)))
            self.data.solar_panel1_voltage.append(float(match.group(9)))
            self.data.solar_panel1_current.append(float(match.group(10)))
            self.data.solar_panel2_state.append(int(match.group(11)))
            self.data.solar_panel2_voltage.append(float(match.group(12)))
            self.data.solar_panel2_current.append(float(match.group(13)))
            self.data.solar_panel3_state.append(int(match.group(14)))
            self.data.solar_panel3_voltage.append(float(match.group(15)))
            self.data.solar_panel3_current.append(float(match.group(16)))
            self.data.solar_panel4_state.append(int(match.group(17)))
            self.data.solar_panel4_voltage.append(float(match.group(18)))
            self.data.solar_panel4_current.append(float(match.group(19)))
            self.data.wind_turbine1_state.append(int(match.group(20)))
            self.data.wind_turbine1_voltage.append(float(match.group(21)))
            self.data.wind_turbine1_current.append(float(match.group(22)))
            self.data.wind_turbine2_state.append(int(match.group(23)))
            self.data.wind_turbine2_voltage.append(float(match.group(24)))
            self.data.wind_turbine2_current.append(float(match.group(25)))
            self.data.fuel_cell1_state.append(int(match.group(26)))
            self.data.fuel_cell1_voltage.append(float(match.group(27)))
            self.data.fuel_cell1_current.append(float(match.group(28)))
            self.data.fuel_cell2_state.append(int(match.group(29)))
            self.data.fuel_cell2_voltage.append(float(match.group(30)))
            self.data.fuel_cell2_current.append(float(match.group(31)))
            self.data.battery_bank1_temperature.append(float(match.group(32)))
            self.data.battery_bank1_voltage.append(float(match.group(33)))
            self.data.battery_bank1_current.append(float(match.group(34)))
            self.data.battery_bank2_temperature.append(float(match.group(35)))
            self.data.battery_bank2_voltage.append(float(match.group(36)))
            self.data.battery_bank2_current.append(float(match.group(37)))
            self.data.battery_bank3_temperature.append(float(match.group(38)))
            self.data.battery_bank3_voltage.append(float(match.group(39)))
            self.data.battery_bank3_current.append(float(match.group(40)))
            self.data.battery_bank4_temperature.append(float(match.group(41)))
            self.data.battery_bank4_voltage.append(float(match.group(42)))
            self.data.battery_bank4_current.append(float(match.group(43)))
            self.data.external_voltage.append(float(match.group(44)))
            self.data.external_current.append(float(match.group(45)))
            self.data.internal_voltage.append(float(match.group(46)))
            self.data.internal_current.append(float(match.group(47)))
            self.data.internal_temperature.append(float(match.group(48)))
            self.data.fuel_cell_volume.append(float(match.group(49)))
            self.data.seawater_ground_state.append(int(match.group(50)))
            self.data.seawater_ground_positve.append(float(match.group(51)))
            self.data.seawater_ground_negative.append(float(match.group(52)))
            self.data.cvt_state.append(int(match.group(53)))
            self.data.cvt_voltage.append(float(match.group(54)))
            self.data.cvt_current.append(float(match.group(55)))
            self.data.cvt_interlock.append(int(match.group(56)))
            self.data.cvt_temperature.append(float(match.group(57)))
            self.data.error_flag3.append(int(match.group(58), 16))


def main(argv=None):
    # load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)
    pwrsys_type = args.switch

    # Initialize the Parser object for the Power System (PWRSYS). No default is set, this has to be entered.
    try:
        pwrsys = Parser(infile, pwrsys_type)
    except ValueError as e:
        print(SWITCH_ERROR)
        return None

    # load the data into a buffered object and parse the data into a dictionary
    pwrsys.load_ascii()
    pwrsys.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(pwrsys.data.toJSON())


if __name__ == '__main__':
    main()
