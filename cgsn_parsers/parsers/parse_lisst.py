"""
@package cgsn_parsers.parsers.parse_lisst
@file cgsn_parsers/parsers/parse_lisst.py
@author Samuel Dahlberg
@brief Parses LISST data logged by the WHOI LISST data logger.
"""
import os
import re

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, FLOAT, NEWLINE, INTEGER

# Regex for the 31 columns of data representing the different volume concentration size classes
size_classes = r'(([+-]?\d+.\d+[Ee]?[+-]?\d*)(,([+-]?\d+.\d+[Ee]?[+-]?\d*)){35})'

# Full Regex pattern
PATTERN = (
    DCL_TIMESTAMP + r'\s' +                     # Time-Stamp
    size_classes + r',' +                       # 36 Column data for particle concentration
    FLOAT + r',' +                              # Laser transmission Sensor [mW]
    FLOAT + r',' +                              # Supply voltage in [V]
    FLOAT + r',' +                              # External analog input 1 [V]
    FLOAT + r',' +                              # Laser Reference sensor [mW]
    FLOAT + r',' +                              # Depth in [m of sea water]
    FLOAT + r',' +                              # Temperature [C]
    INTEGER + r',' +                            # Year
    INTEGER + r',' +                            # Month
    INTEGER + r',' +                            # Day
    INTEGER + r',' +                            # Hour
    INTEGER + r',' +                            # Minute
    INTEGER + r',' +                            # Second
    FLOAT + r',' +                              # External analog input 2 [V]
    FLOAT + r',' +                              # Mean Diameter [μm]
    FLOAT + r',' +                              # Total Volume Concentration [PPM]
    INTEGER + r',' +                            # Relative Humidity [%]
    INTEGER + r',' +                            # Accelerometer X
    INTEGER + r',' +                            # Accelerometer Y
    INTEGER + r',' +                            # Accelerometer Z
    INTEGER + r',' +                            # Raw pressure [overflow single bit]
    INTEGER + r',' +                            # Raw pressure [least significant 16 bits]
    INTEGER + r',' +                            # Ambient Light [counts]
    FLOAT + r',' +                              # External analog input 3 [V]
    FLOAT + r',' +                              # Computed optical transmission over path [dimensionless]
    FLOAT                                       # Beam-attenuation (c) [m-1]
)

REGEX = re.compile(PATTERN, re.DOTALL)

_parameter_names_lisst = [
        'date_time_string',
        'lisst_volume_concentration',
        'laser_transmission_sensor',
        'supply_voltage',
#       'analog_input_1',              # Removed from list, will never have a fluorometer input used
        'laser_reference_sensor',
        'depth',
        'temperature',
        'year',
        'month',
        'day',
        'hour',
        'minute',
        'second',
#       'analog_input_2',              # Removed from list, will never have a fluorometer input used
        'mean_diameter',
        'total_volume_concentation',
        'relative_humidity',
#       'x_accel_counts',              # Removed from list, they are not calibrated or used
#       'y_accel_counts',              # Removed from list, they are not calibrated or used
#       'z_accel_counts',              # Removed from list, they are not calibrated or used
        'pressure',
        'ambient_light',
#       'analog_input_3',              # Removed from list, will never have a fluorometer input used
        'computed_optical_transmission',
        'beam_attenuation'                  
]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the LISST specific
    methods to parse the data, and extracts the LISST data records from the DCL
    daily log files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_lisst)

    def parse_data(self):
        """
        Iterate through the record lines (defined via the regex expression
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
        # Use the date_time_string to calculate an epoch timestamp (seconds
        # since 1970-01-01)
        epts = dcl_to_epoch(match.group(1))
        self.data.time.append(epts)
        self.data.date_time_string.append(str(match.group(1)))

        # Create a list of the 36 columns of volume concentration data and assign to parameter
        data = (match.group(2)).split(',')
        data = list(map(float, data))
        self.data.lisst_volume_concentration.append(data)

        # Assign the remaining lisst data to the named parameters
        self.data.laser_transmission_sensor.append(float(match.group(6)))
        self.data.supply_voltage.append(float(match.group(7)))
        #self.data.analog_input_1.append(float(match.group(8)))
        self.data.laser_reference_sensor.append(float(match.group(9)))
        self.data.depth.append(float(match.group(10)))
        self.data.temperature.append(float(match.group(11)))
        self.data.year.append(int(match.group(12)))
        self.data.month.append(int(match.group(13)))
        self.data.day.append(int(match.group(14)))
        self.data.hour.append(int(match.group(15)))
        self.data.minute.append(int(match.group(16)))
        self.data.second.append(int(match.group(17)))
        # self.data.analog_input_2.append(float(match.group(18)))
        self.data.mean_diameter.append(float(match.group(19)))
        self.data.total_volume_concentation.append(float(match.group(20)))
        self.data.relative_humidity.append(int(match.group(21)))
        # self.data.x_accel_counts.append(int(match.group(22)))
        # self.data.y_accel_counts.append(int(match.group(23)))
        # self.data.z_accel_counts.append(int(match.group(24)))

        # Combining the two outputs for raw pressure into one output.
        overflow = int(match.group(25))
        pressure = int(match.group(26))
        if overflow == 1:
            overflow = 65536
        pressure = pressure + overflow

        self.data.raw_pressure.append(int(pressure))
        self.data.ambient_light.append(int(match.group(27)))
        # self.data.analog_input_3.append(float(match.group(28)))
        self.data.computed_optical_transmission.append(float(match.group(29)))
        self.data.beam_attenuation.append(float(match.group(30)))


def main(argv=None):
    # load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for LISST
    lisst = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    lisst.load_ascii()
    lisst.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(lisst.data.toJSON())

if __name__ == '__main__':
    main()
