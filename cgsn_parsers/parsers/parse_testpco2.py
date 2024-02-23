#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_testpco2
@file cgsn_parsers/parsers/parse_testpco2.py
@author Christopher Wingard
@brief Parses PCO2 data from the Pro-Oceanus pCO2-Pro CV test unit logged by
    the custom-built WHOI data loggers.
"""
import os
import re

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLOAT, INTEGER, NEWLINE

# Regex pattern for a line with a DCL time stamp and a data sentence from the updated PCO2 firmware data.
pattern = (
    DCL_TIMESTAMP + r'\s+' +                   # DCL Time-Stamp
    r'W M,' +                                  # co2_source (always W) and start of measurement string
    r'(\d{4}),(\d{2}),(\d{2}),' +              # PCO2 comma-delimited year, month, day
    r'(\d{2}),(\d{2}),(\d{2}),' +              # PCO2 comma-delimited hour, minute, second
    INTEGER + r',' +                           # zero_a2d
    INTEGER + r',' +                           # current_a2d
    FLOAT + r',' +                             # measured_co2
    FLOAT + r',' +                             # avg_irga_temperature
    FLOAT + r',' +                             # humidity
    FLOAT + r',' +                             # humidity_temperature
    INTEGER + r',' +                           # gas_stream_pressure
    FLOAT + NEWLINE                            # supply voltage
)
REGEX = re.compile(pattern, re.DOTALL)

_parameter_names_testpco2 = [
        'dcl_date_time_string',
        'sensor_time',
        'zero_a2d',
        'current_a2d',
        'measured_water_co2',
        'avg_irga_temperature',
        'humidity',
        'humidity_temperature',
        'gas_stream_pressure',
        'supply_voltage'
    ]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the PCO2 specific
    methods to parse the data,and extracts the PCO2 data records from the DCL
    daily log files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_testpco2)

    def parse_data(self):
        """
        Iterate through the record lines (defined via the regex expressions
        above) in the data object, and parse the data into a pre-defined
        dictionary object created using the Bunch class.
        """
        for line in self.raw:
            match = REGEX.match(line)
            if match:
                self._build_parsed_values(match)

    def _build_parsed_values(self, match):
        """
        Extract the data from the relevant regex groups and assign to elements
        of the data dictionary.
        """
        # Use the DCL date_time_string to calculate an epoch timestamp (seconds since 1970-01-01)
        epts = dcl_to_epoch(match.group(1))
        self.data.time.append(epts)
        self.data.dcl_date_time_string.append(str(match.group(1)))

        # Assign the remaining PCO2 data to the named parameters
        date_string = (match.group(2) + '/' + match.group(3) + '/' + match.group(4) + ' ' +
                       match.group(5) + ':' + match.group(6) + ':' + match.group(7) + '.000')
        co2_time = dcl_to_epoch(date_string)
        self.data.sensor_time.append(co2_time)
        self.data.zero_a2d.append(int(match.group(8)))
        self.data.current_a2d.append(int(match.group(9)))
        self.data.measured_water_co2.append(float(match.group(10)))
        self.data.avg_irga_temperature.append(float(match.group(11)))
        self.data.humidity.append(float(match.group(12)))
        self.data.humidity_temperature.append(float(match.group(13)))
        self.data.gas_stream_pressure.append(int(match.group(14)))
        self.data.supply_voltage.append(float(match.group(15)))


def main(argv=None):
    # load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for PCO2
    pco2 = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    pco2.load_ascii()
    pco2.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(pco2.data.toJSON())


if __name__ == '__main__':
    main()
