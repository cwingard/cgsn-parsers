#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_nutnr
@file cgsn_parsers/parsers/parse_nutnr.py
@author Christopher Wingard
@brief Parses NUTNR data logged by the custom built WHOI data loggers.
"""
import os
import re

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, INTEGER, FLOAT, STRING, NEWLINE

# Set regex string to just find the NUTNR data.
PATTERN = (
    DCL_TIMESTAMP + r'\s+' +         # DCL Time-Stamp
    r'SAT(\w{3})' + r'(\d{4}),' +    # Measurement type and serial #
    STRING + NEWLINE                 # rest of the data, comma separated
)
REGEX = re.compile(PATTERN, re.DOTALL)

# Set an error message string for use when testing the parser switch.
SWITCH_ERROR = 'The NUTNR instrument type must be a string set as either isus, isus_condensed or suna.'


def _parameter_names_nutnr(nutnr_type):
    """
    Setup parameter names for the ISUS (depends on the spectral output, condensed or full), or the SUNA
    """
    # all of the NUTNRs will contain ...
    parameter_names = [
            'date_time_string',
            'measurement_type',
            'serial_number',
            'date_string',
            'decimal_hours',
            'nitrate_concentration',
    ]

    if nutnr_type == 'isus_condensed' or nutnr_type == 'isus':
        # both the condensed and full ASCII data frames for the ISUS contain ...
        parameter_names.extend([
            'auxiliary_fit_1st',
            'auxiliary_fit_2nd',
            'auxiliary_fit_3rd',
            'rms_error'
        ])

        # with the full ASCII frame also having ...
        if nutnr_type == 'isus':
            parameter_names.extend([
                'temperature_internal',
                'temperature_spectrometer',
                'temperature_lamp',
                'lamp_on_time',
                'humidity',
                'voltage_lamp',
                'voltage_analog',
                'voltage_main',
                'average_reference',
                'variance_reference',
                'seawater_dark',
                'spectral_average',
                'channel_measurements'
            ])

    if nutnr_type == 'suna':
        # otherwise we are working with a SUNA, which has ...
        parameter_names.extend([
            'nitrogen_in_nitrate',
            'absorbance_254',
            'absorbance_250',
            'bromide_trace',
            'spectral_average',
            'dark_value',
            'integration_factor',
            'channel_measurements',
            'temperature_internal',
            'temperature_spectrometer',
            'temperature_lamp',
            'lamp_on_time',
            'humidity',
            'voltage_main',
            'voltage_lamp',
            'voltage_internal',
            'main_current',
            'fit_auxiliary_1',
            'fit_auxiliary_2',
            'fit_base_1',
            'fit_base_2',
            'fit_rmse'
        ])

    return parameter_names


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the NUTNR specific methods to parse the data, and extracts
    the NUTNR data records from the DCL daily log files.
    """
    def __init__(self, infile, nutnr_type):
        # test the nutnr_type to make sure it is a string
        try:
            nutnr_type = nutnr_type.lower()
        except ValueError as e:
            print(SWITCH_ERROR)

        # test nutnr_type to make sure it is one of our recognized instruments
        if nutnr_type == 'suna' or nutnr_type == 'isus' or nutnr_type == 'isus_condensed':
            self.nutnr_type = nutnr_type
            self.initialize(infile, _parameter_names_nutnr(self.nutnr_type))
        else:
            raise ValueError()

    def parse_data(self):
        """
        Iterate through the record lines (defined via the regex expression above) in the data object, and parse the
        data into a pre-defined dictionary object created using the Bunch class.
        """
        for line in self.raw:
            match = REGEX.match(line)
            if match:
                self._build_parsed_values(match)

    def _build_parsed_values(self, match):
        """
        Extract the data from the relevant regex groups and assign to elements of the data dictionary.
        """
        # Use the date_time_string to calculate an epoch timestamp (seconds since 1970-01-01)
        epts = dcl_to_epoch(match.group(1))
        self.data.time.append(epts)
        self.data.date_time_string.append(str(match.group(1)))

        # Assign the remaining NUTNR data to the named parameters
        self.data.measurement_type.append(str(match.group(2)))
        self.data.serial_number.append(int(match.group(3)))

        # The rest of the data is in a comma separated string, so...
        data = (match.group(4)).split(',')
        data = [x for x in data if x.strip()]    # drop empty strings found near end of a suna data frame

        self.data.date_string.append(str(data[0]))
        self.data.decimal_hours.append(float(data[1]))
        self.data.nitrate_concentration.append(float(data[2]))

        # ISUS Condensed or Full
        if self.nutnr_type == 'isus_condensed' or self.nutnr_type == 'isus':
            self.data.auxiliary_fit_1st.append(float(data[3]))
            self.data.auxiliary_fit_2nd.append(float(data[4]))
            self.data.auxiliary_fit_3rd.append(float(data[5]))
            self.data.rms_error.append(float(data[6]))

            # Add the additional parameters if a full ISUS data sentence
            if self.nutnr_type == 'isus':
                self.data.temperature_internal.append(float(data[7]))
                self.data.temperature_spectrometer.append(float(data[8]))
                self.data.temperature_lamp.append(float(data[9]))
                self.data.lamp_on_time.append(int(data[10]))
                self.data.humidity.append(float(data[11]))
                self.data.voltage_lamp.append(float(data[12]))
                self.data.voltage_analog.append(float(data[13]))
                self.data.voltage_main.append(float(data[14]))
                self.data.average_reference.append(float(data[15]))
                self.data.variance_reference.append(float(data[16]))
                self.data.seawater_dark.append(float(data[17]))
                self.data.spectral_average.append(float(data[18]))
                self.data.channel_measurements.append(list(map(int, data[19:-1])))

        # SUNA Full
        if self.nutnr_type == 'suna':
            self.data.nitrogen_in_nitrate.append(float(data[3]))
            self.data.absorbance_254.append(float(data[4]))
            self.data.absorbance_250.append(float(data[5]))
            self.data.bromide_trace.append(float(data[6]))
            self.data.spectral_average.append(int(data[7]))
            self.data.dark_value.append(int(data[8]))
            self.data.integration_factor.append(int(data[9]))
            self.data.channel_measurements.append(list(map(int, data[10:266])))
            self.data.temperature_internal.append(float(data[266]))
            self.data.temperature_spectrometer.append(float(data[267]))
            self.data.temperature_lamp.append(float(data[268]))
            self.data.lamp_on_time.append(int(data[269]))
            self.data.humidity.append(float(data[270]))
            self.data.voltage_main.append(float(data[271]))
            self.data.voltage_lamp.append(float(data[272]))
            self.data.voltage_internal.append(float(data[273]))
            self.data.main_current.append(int(data[274]))
            self.data.fit_auxiliary_1.append(float(data[275]))
            self.data.fit_auxiliary_2.append(float(data[276]))
            self.data.fit_base_1.append(float(data[277]))
            self.data.fit_base_2.append(float(data[278]))
            self.data.fit_rmse.append(float(data[279]))


def main(argv=None):
    # load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)
    nutnr_type = args.switch

    # initialize the Parser object for NUTNR, set default type to SUNA if no switch was input
    if nutnr_type:
        try:
            nutnr = Parser(infile, nutnr_type)
        except ValueError as e:
            print(SWITCH_ERROR)
            return None
    else:
        nutnr = Parser(infile, 'suna')

    # load the data into a buffered object and parse the data into a dictionary
    nutnr.load_ascii()
    nutnr.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(nutnr.data.toJSON())


if __name__ == '__main__':
    main()
