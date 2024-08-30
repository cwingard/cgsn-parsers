#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_rbrq3
@file cgsn_parsers/parsers/parse_rbrq3.py
@author Paul Whelan
@brief Parses ADCPU (Nortek Aquadopp) data logged by the custom built WHOI data loggers.


"""
import os
import re
import copy
import pandas as pd
from calendar import timegm
from munch import Munch as Bunch

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, INTEGER, FLOAT, STRING, NEWLINE

HEXINTEGER = r'([0-9|A-F|a-f]+)'             # hex integer
OPT_FLOAT = r'([+-]?\d+.\d+[Ee]?[+-]?\d*)?'  # optional float
OPT_INTEGER = r'([+-]?[0-9]+)?'              # optional integer


# Regex pattern for configuration information

CONFIG_PATTERN = (
    DCL_TIMESTAMP + r'\s' +            # DCL date time stamp
    r'\$PNORI' + r',' +                # Message type: $PNORI,$PNORS,$PNORC
    INTEGER + r',' +                   # Instrument type: 0,2,4 (Aquad,Prof,Sig)
    r'([\w\s]+)' + r',' +              # Instrument name and version
    INTEGER + r',' +                   # Number of beams
    INTEGER + r',' +                   # Number of cells
    FLOAT + r',' +                     # Blanking (m)
    FLOAT + r',' +                     # Cell size (m)
    r'([0-9])' +                       # Coord System 0=ENU,1=XYZ,2=BEAM
    r'\*' +
    HEXINTEGER +                          # Checksum                 
    NEWLINE
)
CONFIG_REGEX = re.compile( CONFIG_PATTERN, re.DOTALL )

# Regex pattern for sensor data

SENSOR_PATTERN = (
    DCL_TIMESTAMP + r'\s' +            # DCL date time stamp
    r'\$PNORS' + r',' +                # Message type: $PNORI,$PNORS,$PNORC
    INTEGER + r',' +                   # Date: MMDDYY
    INTEGER + r',' +                   # Time: HHMMSS
    HEXINTEGER + r',' +                # Error code: hex
    HEXINTEGER + r',' +                # Status code: hex
    FLOAT + r',' +                     # Battery voltage
    FLOAT + r',' +                     # Sound speed
    FLOAT + r',' +                     # Heading
    FLOAT + r',' +                     # Pitch
    FLOAT + r',' +                     # Roll
    FLOAT + r',' +                     # Pressure
    FLOAT + r',' +                     # Temperature
    INTEGER + r',' +                   # Analog input 1
    INTEGER +                          # Analog input 2
    r'\*' +
    HEXINTEGER +                          # Checksum                 
    NEWLINE
)
SENSOR_REGEX = re.compile( SENSOR_PATTERN, re.DOTALL )

# Regex pattern for current data

CURRENT_PATTERN = (
    DCL_TIMESTAMP + r'\s' +            # DCL date time stamp
    r'\$PNORC' + r',' +                # Message type: $PNORI,$PNORS,$PNORC
    INTEGER + r',' +                   # Date: MMDDYY
    INTEGER + r',' +                   # Time: HHMMSS
    INTEGER + r',' +                   # Cell number
    FLOAT + r',' +                     # Velocity beam 1
    FLOAT + r',' +                     # Velocity beam 2
    FLOAT + r',' +                     # Velocity beam 3
    OPT_FLOAT + r',' +                 # Velocity beam 4
    FLOAT + r',' +                     # Speed (m/s)
    FLOAT + r',' +                     # Direction (dg)
    r'([A-Za-z])' + r',' +             # Amplitude units C-counts
    INTEGER + r',' +                   # Amplitude beam 1
    INTEGER + r',' +                   # Amplitude beam 2
    INTEGER + r',' +                   # Amplitude beam 3
    OPT_INTEGER + r',' +               # Amplitude beam 4
    INTEGER + r',' +                   # Correlation % beam 1
    INTEGER + r',' +                   # Correlation % beam 2
    INTEGER + r',' +                   # Correlation % beam 3
    OPT_INTEGER +                      # Correlation % beam 4
    r'\*' +
    HEXINTEGER +                          # Checksum                 
    NEWLINE
)
CURRENT_REGEX = re.compile( CURRENT_PATTERN, re.DOTALL )

# ADCPU parameter data for data format 100 / NMEA

class ParameterNames(object):
    """
    Nortek Aquadopp parameter names using Data format 100, NMEA
    """
    def __init__(self):

        # Config Information Data
        self._config = [
            'dcl_datetime',
            'instrument_type',
            'instrument_name',
            'number_beams',
            'number_cells',
            'blanking',
            'cell_size',
            'coord_system'
        ]

        # Sensor data
        self._sensor = [
            'dcl_datetime',
            'sensor_datetime',
            'error_code',
            'status_code',
            'battery_voltage',
            'sound_speed',
            'heading',
            'pitch',
            'roll',
            'pressure',
            'temperature',
            'analog_in_1',
            'analog_in_2'
        ]

        # Current Data
        self._current = [
            'dcl_datetime',
            'sensor_datetime',
            'cell_number',
            'velocity_beam_1',
            'velocity_beam_2',
            'velocity_beam_3',
            'velocity_beam_4',
            'speed',
            'direction',
            'amplitude_units',
            'amplitude_beam_1',
            'amplitude_beam_2',
            'amplitude_beam_3',
            'amplitude_beam_4',
            'correlation_beam_1',
            'correlation_beam_2',
            'correlation_beam_3',
            'correlation_beam_4'
        ]


    # Create the initial dictionary object from the config, sensor and current.

    def create_dict(self):
        """
        Create a Bunch class object to store the parameter names for the
        Workhorse ADCP pd0 data files, with the data organized hierarchically
        by the data type.
        """
        bunch = Bunch()
        bunch.time = []
        bunch.config = Bunch()
        bunch.sensor= Bunch()
        bunch.current = Bunch()
        bunch.cells = {}         # runtime sized

        for name in self._config:
            bunch.config[name] = []

        for name in self._sensor:
            bunch.sensor[name] = []

        for name in self._current:
            bunch.current[name] = []

        return bunch


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the adcpu specific
    methods to parse the data, and extracts the adcpu records from the DCL
    daily log files.
    """
    def __init__(self, infile):

        self.initialize(infile, [])

        data = ParameterNames()

        self.data = data.create_dict()


    def parse_data(self):
        """
        Iterate through the record lines (defined via the regex expression
        above) in the data object, and parse the data into a pre-defined
        dictionary object created using the Bunch class.
        """
        for line in self.raw:
            match = CONFIG_REGEX.match(line)
            if match:
                self._build_config_parsed_values(match)
                continue

            match = SENSOR_REGEX.match(line)
            if match:
                self._build_sensor_parsed_values(match)
                continue

            match = CURRENT_REGEX.match(line)
            if match:
                self._build_current_parsed_values(match)
                continue


    def _build_config_parsed_values(self, match):
        """
        Extract the data from the config regex groups and assign to elements
        of the data dictionary.
        """

        # Assign the DCL date_time_string
        self.data.config.dcl_datetime.append(match.group(1))
        
        self.data.config.instrument_type.append(int(match.group(2)))

        self.data.config.instrument_name.append(match.group(3))

        self.data.config.number_beams.append(int(match.group(4)))

        self.data.config.number_cells.append(int(match.group(5)))

        self.data.config.blanking.append(float(match.group(6)))

        self.data.config.cell_size.append(float(match.group(7)))

        self.data.config.coord_system.append(int(match.group(8)))

        # Use the number of cells to size the cells dictionary if not yet done
        # Populate it with fields from the "current" dictionary
        
        if len(self.data.cells) == 0:
            num_cells = int(match.group(5))
            for i in range(num_cells):
                self.data.cells[str(i+1)] = copy.deepcopy(self.data.current)

        
    def _build_sensor_parsed_values(self, match):
        """
        Extract the data from the sensor regex groups and assign to elements
        of the data dictionary.
        """

        # Assign the DCL date_time_string
        self.data.sensor.dcl_datetime.append(match.group(1))
        
        # Compute and use unix time from sensor date and time
        sensor_date_time = match.group(2) + ' ' + match.group(3)
        date_time = pd.to_datetime(sensor_date_time, format='%m%d%y %H%M%S', exact=False, utc=True)
        unix_time = timegm(date_time.timetuple())    
        self.data.time.append(unix_time)
        self.data.sensor.sensor_datetime.append(unix_time)

        self.data.sensor.error_code.append(match.group(4))

        self.data.sensor.status_code.append(match.group(5))

        self.data.sensor.battery_voltage.append(float(match.group(6)))

        self.data.sensor.sound_speed.append(float(match.group(7)))

        self.data.sensor.heading.append(float(match.group(8)))

        self.data.sensor.pitch.append(float(match.group(9)))

        self.data.sensor.roll.append(float(match.group(10)))

        self.data.sensor.pressure.append(float(match.group(11)))

        self.data.sensor.temperature.append(float(match.group(12)))

        self.data.sensor.analog_in_1.append(int(match.group(13)))

        self.data.sensor.analog_in_2.append(int(match.group(14)))


    def _build_current_parsed_values(self, match):
        """
        Extract the data from the current regex groups and assign to elements
        of the data dictionary.
        """
        cell_number = match.group(4)

        # Assign the DCL date_time_string
        self.data.cells[cell_number].dcl_datetime.append(match.group(1))
        
        # Compute and use unix time from sensor date and time
        sensor_date_time = match.group(2) + ' ' + match.group(3)
        date_time = pd.to_datetime(sensor_date_time, format='%m%d%y %H%M%S', exact=False, utc=True)
        unix_time = timegm(date_time.timetuple())    
        self.data.cells[cell_number].sensor_datetime.append(unix_time)

        self.data.cells[cell_number].cell_number = int(cell_number)
        self.data.cells[cell_number].velocity_beam_1.append(float(match.group(5)))
        self.data.cells[cell_number].velocity_beam_2.append(float(match.group(6)))
        self.data.cells[cell_number].velocity_beam_3.append(float(match.group(7)))
        if match.group(8) is not None:
            self.data.cells[cell_number].velocity_beam_4.append(float(match.group(8)))
        else:
            self.data.cells[cell_number].velocity_beam_4.append(float('NaN'))

        self.data.cells[cell_number].speed.append(float(match.group(9)))
        self.data.cells[cell_number].direction.append(float(match.group(10)))
        self.data.cells[cell_number].amplitude_units.append(match.group(11))

        self.data.cells[cell_number].amplitude_beam_1.append(int(match.group(12)))
        self.data.cells[cell_number].amplitude_beam_2.append(int(match.group(13)))
        self.data.cells[cell_number].amplitude_beam_3.append(int(match.group(14)))
        if match.group(15) is not None:
            self.data.cells[cell_number].amplitude_beam_4.append(int(match.group(15)))
        else:
            self.data.cells[cell_number].amplitude_beam_4.append(0)

        self.data.cells[cell_number].correlation_beam_1.append(int(match.group(16)))
        self.data.cells[cell_number].correlation_beam_2.append(int(match.group(17)))
        self.data.cells[cell_number].correlation_beam_3.append(int(match.group(18)))
        if match.group(19) is not None:
            self.data.cells[cell_number].correlation_beam_4.append(int(match.group(19)))
        else:
            self.data.cells[cell_number].correlation_beam_4.append(0)


def main(argv=None):
    # load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for adcpu
    adcpu = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    adcpu.load_ascii()
    adcpu.parse_data()

    # The current dictionary was just used to prime cell dictionaries. Lose it.
    del adcpu.data['current']

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(adcpu.data.toJSON())

if __name__ == '__main__':
    main()
