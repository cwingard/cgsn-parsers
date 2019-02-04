#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_wavss
@file cgsn_parsers/parsers/parse_wavss.py
@author Christopher Wingard
@brief Parses the summary and spectral wave data from the TriAxys Wave Sensor
    logged by the custom built CGSN data loggers.
"""
import os
import re

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP, INTEGER, FLOAT, NEWLINE, STRING

# Set an error message string for use when testing the parser switch.
SWITCH_ERROR = 'The correct WAVSS NMEA data sentence must be entered for the parser to correctly function.'

def _parameter_names_wavss(nmea_sentence):
    """
    Setup the parameter names for the WAVSS based upon the NMEA data sentences
    """
    # all of the NMEA data sentences will contain ...
    parameter_names = [
        'dcl_date_time_string',
        'date_string',
        'time_string',
        'serial_number'
    ]

    if nmea_sentence == 'TSPWA':
        # Parameters for the summary wave statistics
        parameter_names.extend([
            'num_zero_crossings',
            'average_wave_height',
            'mean_spectral_period',
            'maximum_wave_height',
            'significant_wave_height',
            'significant_wave_period',
            'average_tenth_height',
            'average_tenth_period',
            'average_wave_period',
            'peak_period',
            'peak_period_read',
            'spectral_wave_height',
            'mean_wave_direction',
            'mean_directional_spread'
        ])

    if nmea_sentence == 'TSPNA':
        # Parameters for the non-directional spectra
        parameter_names.extend([
            'number_bands',
            'initial_frequency',
            'frequency_spacing',
            'energy'
        ])

    if nmea_sentence == 'TSPMA':
        # Parameters for the mean directional spectra
        parameter_names.extend([
            'number_bands',
            'initial_frequency',
            'frequency_spacing',
            'average_direction',
            'spread_direction',
            'energy',
            'directional_mean',
            'directional_spread'
        ])

    if nmea_sentence == 'TSPFB':
        # Parameters for the fourier coefficients
        parameter_names.extend([
            'number_bands',
            'initial_frequency',
            'frequency_spacing',
            'number_directional_bands',
            'initial_directional_frequency',
            'directional_frequency_spacing',
            'a1_band',
            'b1_band',
            'a2_band',
            'b2_band'
        ])

    if nmea_sentence == 'TSPHA':
        # Parameters for the heave, north, east data
        parameter_names.extend([
            'number_samples',
            'initial_time',
            'time_spacing',
            'm33_status',
            'heave',
            'north',
            'east'
        ])

    return parameter_names


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the WAVSS specific methods to parse the data,
    and extracts the different wavss data records from the DCL daily log files.
    """
    def __init__(self, infile, nmea_sentence):
        # test the nmea_sentence to make sure it is a string
        try:
            nmea_sentence = nmea_sentence.upper()
        except ValueError as e:
            print(SWITCH_ERROR)

        # test nmea_sentence to make sure it is one of our recognized configurations
        if nmea_sentence in ['TSPWA', 'TSPNA', 'TSPMA', 'TSPFB', 'TSPHA']:
            self.nmea_sentence = nmea_sentence
            self.initialize(infile, _parameter_names_wavss(self.nmea_sentence))
        else:
            raise ValueError(SWITCH_ERROR)

    def parse_data(self):
        """
        Iterate through the record lines (defined via the regex expression above) in the data object, and parse the
        data into a pre-defined dictionary object created using the Bunch class.
        """
        regex = self._nmea_regex()
        for line in self.raw:
            match = regex.match(line)
            if match:
                self._build_parsed_values(match)

    def _nmea_regex(self):
        """
        Creates the regex pattern matcher for the different NMEA data sentences produced by the WAVSS.
        """
        if self.nmea_sentence == 'TSPWA':
            # Regex pattern for a line with a DCL time stamp, possible DCL status value and the wave statistics
            pattern = (
                DCL_TIMESTAMP + r'\s+' +       # DCL Time-Stamp
                r'\$TSPWA,(\d{8}),(\d{6}),' +  # NMEA sentence header and date and time
                r'(\d{5}),(?:buoyID)?,,,' +    # Tri-Axys unit serial number
                INTEGER + r',' +               # Number of Zero Crossings
                FLOAT + r',' +                 # Average wave height (Havg)
                FLOAT + r',' +                 # Tz (Mean Spectral  Period)
                FLOAT + r',' +                 # Hmax (Maximum Wave Height)
                FLOAT + r',' +                 # Hsig (Significant Wave Height)
                FLOAT + r',' +                 # Tsig (Significant Period)
                FLOAT + r',' +                 # H10 (average height of highest 1/10 of waves)
                FLOAT + r',' +                 # T10 (average period of H10 waves)
                FLOAT + r',' +                 # Tavg (Mean Wave Period)
                FLOAT + r',' +                 # TP (Peak Period)
                FLOAT + r',' +                 # TP5
                FLOAT + r',' +                 # HMO
                FLOAT + r',' +                 # Mean Direction
                FLOAT +                        # Mean Spread
                r'\*[0-9a-fA-F]+' + NEWLINE    # checksum and <cr><lf>
            )

        if self.nmea_sentence == 'TSPNA':
            # Regex pattern for a line with a DCL time stamp, possible DCL status value and the non-directional spectra data
            pattern = (
                DCL_TIMESTAMP + r'\s+' +       # DCL Time-Stamp
                r'\$TSPNA,(\d{8}),(\d{6}),' +  # NMEA sentence header and date and time
                r'(\d{5}),(?:buoyID)?,,,' +    # Tri-Axys unit serial number
                INTEGER + r',' +               # Number of bands
                FLOAT + r',' + FLOAT + r',' +  # Initial frequency and frequency spacing
                STRING + NEWLINE               # rest of the data, including the checksum, comma separated
            )

        if self.nmea_sentence == 'TSPMA':
            # Regex pattern for a line with a DCL time stamp, possible DCL status value and the mean directional spectra data
            pattern = (
                DCL_TIMESTAMP + r'\s+' +       # DCL Time-Stamp
                r'\$TSPMA,(\d{8}),(\d{6}),' +  # NMEA sentence header and date and time
                r'(\d{5}),(?:buoyID)?,,,' +    # Tri-Axys unit serial number
                INTEGER + r',' +               # Number of bands
                FLOAT + r','+ FLOAT + r',' +   # Initial frequency and frequency spacing
                FLOAT + r','+ FLOAT + r',' +   # Mean average direction and spread direction
                STRING + NEWLINE               # rest of the data, including the checksum, comma separated
            )

        if self.nmea_sentence == 'TSPFB':
            # Regex pattern for a line with a DCL time stamp, possible DCL status value and the fourier coefficients
            pattern = (
                DCL_TIMESTAMP + r'\s+' +       # DCL Time-Stamp
                r'\$TSPFB,(\d{8}),(\d{6}),' +  # NMEA sentence header and date and time
                r'(\d{5}),(?:buoyID)?,,,' +    # Tri-Axys unit serial number
                INTEGER + r',' +               # Number of bands
                FLOAT + r',' + FLOAT + r',' +  # Initial frequency and frequency spacing
                INTEGER + r',' +               # Number of directional bands
                FLOAT + r',' + FLOAT + r',' +  # Directional initial frequency and directional frequency spacing
                STRING + NEWLINE               # rest of the data, including the checksum, comma separated
            )

        if self.nmea_sentence == 'TSPHA':
            # Regex pattern for a line with a DCL time stamp, possible DCL status value and the heave, north, east data
            pattern = (
                DCL_TIMESTAMP + r'\s+' +       # DCL Time-Stamp
                r'\$TSPHA,(\d{8}),(\d{6}),' +  # NMEA sentence header and date and time
                r'(\d{5}),(?:buoyID)?,,,' +    # Tri-Axys unit serial number
                INTEGER + r',' +               # Number of samples
                FLOAT + r',' + FLOAT + r',' +  # Initial time and time spacing
                INTEGER + r',' +               # M33 status
                STRING + NEWLINE               # rest of the data, including the checksum, comma separated
            )

        regex = re.compile(pattern, re.DOTALL)
        return regex

    def _build_parsed_values(self, match):
        """
        Extract the data from the relevant regex groups and assign to elements of the data dictionary.
        """
        # Use the date_time_string to calculate an epoch timestamp (seconds since
        # 1970-01-01)
        epts = dcl_to_epoch(match.group(1))
        self.data.time.append(epts)
        self.data.dcl_date_time_string.append(str(match.group(1)))
        self.data.date_string.append(str(match.group(2)))
        self.data.time_string.append(str(match.group(3)))
        self.data.serial_number.append(str(match.group(4)))

        # Assign the remaining WAVSS data to the named parameters based upon the NMEA data sentence
        if self.nmea_sentence == 'TSPWA':   # summary wave statistics
            self.data.num_zero_crossings.append(int(match.group(5)))
            self.data.average_wave_height.append(float(match.group(6)))
            self.data.mean_spectral_period.append(float(match.group(7)))
            self.data.maximum_wave_height.append(float(match.group(8)))
            self.data.significant_wave_height.append(float(match.group(9)))
            self.data.significant_wave_period.append(float(match.group(10)))
            self.data.average_tenth_height.append(float(match.group(11)))
            self.data.average_tenth_period.append(float(match.group(12)))
            self.data.average_wave_period.append(float(match.group(13)))
            self.data.peak_period.append(float(match.group(14)))
            self.data.peak_period_read.append(float(match.group(15)))
            self.data.spectral_wave_height.append(float(match.group(16)))
            self.data.mean_wave_direction.append(float(match.group(17)))
            self.data.mean_directional_spread.append(float(match.group(18)))

        if self.nmea_sentence == 'TSPNA':   # non-directional spectra
            self.data.number_bands.append(int(match.group(5)))
            self.data.initial_frequency.append(float(match.group(6)))
            self.data.frequency_spacing.append(float(match.group(7)))
            data = (match.group(8)).replace('*', ',').split(',')[:-1]
            self.data.energy.append([float(x) for x in data])

        if self.nmea_sentence == 'TSPMA':   # mean directional spectra
            self.data.number_bands.append(int(match.group(5)))
            self.data.initial_frequency.append(float(match.group(6)))
            self.data.frequency_spacing.append(float(match.group(7)))
            self.data.average_direction.append(float(match.group(8)))
            self.data.spread_direction.append(float(match.group(9)))
            data = (match.group(10)).replace('*', ',').split(',')[:-1]
            data = [float(x) for x in data]
            self.data.energy.append(data[0::3])
            self.data.directional_mean.append(data[1::3])
            self.data.directional_spread.append(data[2::3])

        if self.nmea_sentence == 'TSPFB':   # mean directional spectra
            self.data.number_bands.append(int(match.group(5)))
            self.data.initial_frequency.append(float(match.group(6)))
            self.data.frequency_spacing.append(float(match.group(7)))
            self.data.number_directional_bands.append(int(match.group(8)))
            self.data.initial_directional_frequency.append(float(match.group(9)))
            self.data.directional_frequency_spacing.append(float(match.group(10)))
            data = (match.group(11)).replace('*', ',').split(',')[:-1]
            data = [float(x) for x in data]
            self.data.a1_band.append(data[0::4])
            self.data.b1_band.append(data[1::4])
            self.data.a2_band.append(data[2::4])
            self.data.b2_band.append(data[3::4])

        if self.nmea_sentence == 'TSPHA':   # heave, north, east
            self.data.number_samples.append(int(match.group(5)))
            self.data.initial_time.append(float(match.group(6)))
            self.data.time_spacing.append(float(match.group(7)))
            self.data.m33_status.append(int(match.group(8)))
            data = (match.group(9)).replace('*', ',').split(',')[:-1]
            data = [float(x) for x in data]
            self.data.heave.append(data[0::3])
            self.data.north.append(data[1::3])
            self.data.east.append(data[2::3])


def parse_waves(infile, nmea_sentence):
    """
    Initialize the Parser object for the WAVSS, using a NMEA sentence that corresponds to the data sentences described
    in the instrument manual.

    :param infile: Input file with raw data to parse.
    :param nmea_sentence: TriAxys (WAVSS) NMEA data sentence to parse
    :return: parsed WAVSS data object
    """
    # initialize the Parser object for the WAVSS specifying the NMEA data sentence to parse
    wavss = Parser(infile, nmea_sentence)

    # load the data into a buffered object and parse the data into a dictionary
    wavss.load_ascii()
    wavss.parse_data()

    return wavss

def main(argv=None):
    # Load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # Parse the different NMEA data sentences out of the WAVSS data file, saving the results in separate data files per
    # data sentence type.
    try:
        wavss = parse_waves(infile, 'TSPWA')   # summary wave statistics
        # save the data to a JSON formatted data file appending the NMEA data sentence type to the file name
        with open(outfile, 'w') as f:
            f.write(wavss.data.toJSON())

        wavss = parse_waves(infile, 'TSPNA')   # non-directional spectra
        # save the data to a JSON formatted data file appending the NMEA data sentence type to the file name
        with open(outfile.replace('.json', '.tspna.json'), 'w') as f:
            f.write(wavss.data.toJSON())

        wavss = parse_waves(infile, 'TSPMA')   # mean directional spectra
        # save the data to a JSON formatted data file appending the NMEA data sentence type to the file name
        with open(outfile.replace('.json', '.tspma.json'), 'w') as f:
            f.write(wavss.data.toJSON())

        wavss = parse_waves(infile, 'TSPFB')   # fourier coefficients
        # save the data to a JSON formatted data file appending the NMEA data sentence type to the file name
        with open(outfile.replace('.json', '.tspfb.json'), 'w') as f:
            f.write(wavss.data.toJSON())

        wavss = parse_waves(infile, 'TSPHA')   # heave, north, east
        # save the data to a JSON formatted data file appending the NMEA data sentence type to the file name
        with open(outfile.replace('.json', '.tspha.json'), 'w') as f:
            f.write(wavss.data.toJSON())
    except Exception as e:
        print('WAVSS parsing failed: {}'.format(e))

if __name__ == '__main__':
    main()
