#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_phtest
@file cgsn_parsers/parsers/parse_phtest.py
@author Christopher Wingard
@brief Parses the 3 pH sensors tested, the ANB OC300, Idronaut Ocean Seven 310
    and the Sea-Bird Deep SeapHOx V2.
"""
import os
import re

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLOAT, INTEGER, NEWLINE

# Set the regex patterns to find the pH data from the sensors.
ANB_PATTERN = (
    DCL_TIMESTAMP + r'\s*' +        # DCL Time-Stamp
    r'$ANB,([A-F0-9]{4}),' +        # Data header and CRC
    r'(\d{4}:\d{2}:\d{2}:\d{2}:\d{2}:\d{2}),' +  # instrument clock
    FLOAT + r',' +                  # pH
    FLOAT + r',' +                  # temperature (degC)
    FLOAT + r',' +                  # salinity (psu)
    FLOAT + r',' +                  # conductivity (mS/cm)
    INTEGER + r',' +                # transducer health
    INTEGER + r',' +                # sensor diagnostics
    INTEGER + r',' +                # reserved for future use (default to 0)
    INTEGER + r',' +                # Modbus address
    INTEGER + r',' +                # file number
    NEWLINE
)

IDRON_PATTERN = (
    DCL_TIMESTAMP + r'\s*' +        # DCL Time-Stamp
    FLOAT + r'\s*' +                # pressure (dbar)
    FLOAT + r'\s*' +                # Temperature (degC)
    FLOAT + r'\s*' +                # conductivity (S/m)
    FLOAT + r'\s*' +                # salinity (psu)
    FLOAT + r'\s*' +                # oxygen (%)
    FLOAT + r'\s*' +                # oxygen (ppm)
    FLOAT + r'\s*' +                # pH
    FLOAT + r'\s*' +                # external reference
    r'(\d{2}:\d{2}:\d{2}.\d{2})' +  # instrument clock
    r'(\S{2})' + NEWLINE            # memory status
)

CPHOX_PATTERN = (
    DCL_TIMESTAMP + r'\s*' +        # DCL Time-Stamp
    r'DSPHOX(\d{5}),' + r'\s*' +    # Serial number
    r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}),' + r'\s*' +  # Instrument clock
    INTEGER + r',\s*' +             # Sample Number
    INTEGER + r',\s*' +             # Error code
    FLOAT + r',\s*' +               # Temperature (degC)
    FLOAT + r',\s*' +               # pH
    FLOAT + r',\s*' +               # external reference electrode (volts)
    FLOAT + r',\s*' +               # pressure (dbar)
    FLOAT + r',\s*' +               # salinity (psu)
    FLOAT + r',\s*' +               # conductivity (mS/cm)
    FLOAT + r',\s*' +               # oxygen (mL/L)
    FLOAT + r',\s*' +               # internal relative humidity (%)
    FLOAT + NEWLINE                 # internal temperature (degC)
)

# Set an error message string for use when testing the parser switch.
SWITCH_ERROR = 'The test pH sensor must be a string set as either anb, idron or cphox (case insensitive).'


def _parameter_names_phtest(ph_type):
    """
    Create the list of parameter names corresponding to the pH sensor being
    used for the test. Options are either the ANB Sensors OC300, the Idronaut
    Ocean Seven 310, or the Sea-Bird Electronics Deep SeapHOx V2.

    :param ph_type: string indicating the ph sensor type
    :return parameter_names: list of parameter names
    """
    if ph_type == 'anb':
        parameter_names = [
            'dcl_date_time_string',
            'checksum',
            'anb_date_time_string',
            'seawater_ph',
            'temperature',
            'salinity',
            'conductivity',
            'transducer_health',
            'sensor_diagnostics',
            # 'reserved',  # keep this in case we need to add it back in
            # 'modbus_address',  # keep this in case we need to add it back in
            'file_number'
        ]
    elif ph_type == 'idron':
        parameter_names = [
            'dcl_date_time_string',
            'pressure',
            'temperature',
            'conductivity',
            'salinity',
            'oxygen_saturation',
            'oxygen_concentration',
            'seawater_ph',
            'external_reference',
            'idron_time_string',
            'memory_status'
        ]
    elif ph_type == 'cphox':
        parameter_names = [
            'dcl_date_time_string',
            'serial_number',
            'cphox_date_time_string',
            'sample_number',
            'error_flag',
            'temperature',
            'seawater_ph',
            'external_reference',
            'pressure',
            'salinity',
            'conductivity',
            'oxygen_concentration',
            'internal_humidity',
            'internal_temperature'
        ]
    else:
        raise ValueError(SWITCH_ERROR)

    return parameter_names


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the specific pH
    sensor methods to parse the data, and extracts the pH data records from
    the DCL daily log files.
    """
    def __init__(self, infile, ph_type):
        # test the ph_type to make sure it is a string
        try:
            ph_type = ph_type.lower()
        except ValueError:
            print(SWITCH_ERROR)

        # test ph_type to make sure it is one of our recognized configurations
        if ph_type in ['idron', 'sphox']:
            self.ph_type = ph_type
            self.initialize(infile, _parameter_names_phtest(self.ph_type))
        else:
            raise ValueError(SWITCH_ERROR)

    def parse_data(self):
        """
        Iterate through the record lines (defined via the regex expression above) in the data object, and parse the
        data into a pre-defined dictionary object created using the Bunch class.
        """
        if self.ph_type == 'anb':
            regex = re.compile(ANB_PATTERN, re.DOTALL)
        elif self.ph_type == 'idron':
            regex = re.compile(IDRON_PATTERN, re.DOTALL)
        elif self.ph_type == 'cphox':
            regex = re.compile(CPHOX_PATTERN, re.DOTALL)
        else:
            raise ValueError(SWITCH_ERROR)

        for line in self.raw:
            match = regex.match(line)
            if match:
                self._build_parsed_values(match)

    def _build_parsed_values(self, match):
        """
        Extract the data from the relevant regex groups and assign to elements of the data dictionary.
        """
        # Use the date_time_string to calculate an epoch timestamp (seconds since
        # 1970-01-01)
        epts = dcl_to_epoch(match.group(1))
        self.data.time.append(epts)
        self.data.dcl_date_time_string.append(str(match.group(1)))

        if self.ph_type == 'anb':
            self.data.checksum.append(str(match.group(2)))
            self.data.anb_date_time_string.append(str(match.group(3)))
            self.data.seawater_ph.append(float(match.group(4)))
            self.data.temperature.append(float(match.group(5)))
            self.data.salinity.append(float(match.group(6)))
            self.data.conductivity.append(float(match.group(7)))
            self.data.transducer_health.append(int(match.group(8)))
            self.data.sensor_diagnostics.append(int(match.group(9)))
            # self.data.reserved.append(int(match.group(10)))  # keep this in case we need to add it back in
            # self.data.modbus_address.append(int(match.group(11)))  # keep this in case we need to add it back in
            self.data.file_number.append(int(match.group(10)))

        if self.ph_type == 'idron':
            self.data.pressure.append(float(match.group(2)))
            self.data.temperature.append(float(match.group(3)))
            self.data.conductivity.append(float(match.group(4)))
            self.data.salinity.append(float(match.group(5)))
            self.data.oxygen_saturation.append(float(match.group(6)))
            self.data.oxygen_concentration.append(float(match.group(7)))
            self.data.seawater_ph.append(float(match.group(8)))
            self.data.external_reference.append(float(match.group(9)))
            self.data.idron_time_string.append(str(match.group(10)))
            self.data.memory_status.append(str(match.group(11)))

        if self.ph_type == 'sphox':
            self.data.serial_number.append(str(match.group(2)))
            self.data.sphox_date_time_string.append(str(match.group(3)))
            self.data.sample_number.append(int(match.group(4)))
            self.data.error_flag.append(str(match.group(5)))
            self.data.temperature.append(float(match.group(6)))
            self.data.seawater_ph.append(float(match.group(7)))
            self.data.external_reference.append(float(match.group(8)))
            self.data.pressure.append(float(match.group(9)))
            self.data.salinity.append(float(match.group(10)))
            self.data.conductivity.append(float(match.group(11)))
            self.data.oxygen_concentration.append(float(match.group(12)))
            self.data.internal_humidity.append(float(match.group(13)))
            self.data.internal_temperature.append(float(match.group(14)))


def main(argv=None):
    # load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)
    ph_type = args.switch

    # initialize the Parser object for the pH data
    try:
        ph = Parser(infile, ph_type)
    except ValueError:
        print(SWITCH_ERROR)
        return None

    # load the data into a buffered object and parse the data into a dictionary
    ph.load_ascii()
    ph.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON formatted data file (note, no pretty-printing
    # keeping things compact)
    with open(outfile, 'w') as f:
        f.write(ph.data.toJSON())


if __name__ == '__main__':
    main()
