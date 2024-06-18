#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.parsers.parse_pco2w
@file cgsn_parsers/parsers/parse_pco2w.py
@author Christopher Wingard
@brief Parses PCO2W data logged by the custom built WHOI data loggers.
"""
import os
import re

# Import common utilities and base classes
from cgsn_parsers.parsers.common import ParserCommon
from cgsn_parsers.parsers.common import dcl_to_epoch, inputs, DCL_TIMESTAMP

# replaced following lines in regex to support sami rev k ( :# insteadn of * )
#    r'(\*[A-F0-9]{4}11[A-F0-9]+)' +                 # Device 1 (external pump) sample collection
#    r'(\*[A-F0-9]{4})(04|05)([A-F0-9]+)'            # Device 0 sample processing


# Regex patterns for PCO2W data logged either via direct polling...
POLLED_PATTERN = (
    DCL_TIMESTAMP + r'\s+' +                        # DCL Time-Stamp
    r'(?:\*|:\d)([A-F0-9]{4}11[A-F0-9]+)' + r'\s' +         # Device 1 (external pump) sample collection
    DCL_TIMESTAMP + r'\s+' +                        # DCL Time-Stamp
    r'(?:\*|:\d)([A-F0-9]{4})(04|05)([A-F0-9]+)'            # Device 0 sample processing
)
POLLED_REGEX = re.compile(POLLED_PATTERN, re.DOTALL)


# ...or if the unit is configured to run autonomously.

# replaced the following lines in regex to support sami rev k ( :# instead of * )
#    r'(\*[A-F0-9]{4}11[A-F0-9]+)' +                 # Device 1 (external pump) sample collection
#    r'(\*[A-F0-9]{4})(04|05)([A-F0-9]+)'            # Device 0 sample processing

AUTO_PATTERN = (
    DCL_TIMESTAMP + r'\s+' +                        # DCL Time-Stamp
    r'(?:\*|:\d)([A-F0-9]{4}11[A-F0-9]+)' +                 # Device 1 (external pump) sample collection
    r'[\s\S]*?' +                                    # Nonessential text and lines between samples
    DCL_TIMESTAMP + r'\s+' +                        # DCL Time-Stamp
    r'(?:\*|:\d)([A-F0-9]{4})(04|05)([A-F0-9]+)'            # Device 0 sample processing
)
AUTO_REGEX = re.compile(AUTO_PATTERN, re.DOTALL)

_parameter_names_pco2w = [
    'collect_date_time',
    'process_date_time',
    'unique_id',
    'record_length',
    'record_type',
    'record_time',
    'dark_reference_a',
    'dark_signal_a',
    'reference_434_a',
    'signal_434_a',
    'reference_620_a',
    'signal_620_a',
    'ratio_434',
    'ratio_620',
    'dark_reference_b',
    'dark_signal_b',
    'reference_434_b',
    'signal_434_b',
    'reference_620_b',
    'signal_620_b',
    'voltage_raw',
    'thermistor_raw'
]


class Parser(ParserCommon):
    """
    A Parser subclass that calls the Parser base class, adds the pco2w specific
    methods to parse the data, and extracts the pco2w data records from the DCL
    daily log files.
    """
    def __init__(self, infile):
        self.initialize(infile, _parameter_names_pco2w)

    def parse_data(self):
        """
        Iterate through the record markers (defined via the regex expression
        above) in the data object, and parse the data file into a pre-defined
        dictionary object created using the Bunch class.
        """
        raw = ''.join(self.raw)
        polled_marker = [m.start() for m in POLLED_REGEX.finditer(raw)]
        auto_marker = [m.start() for m in AUTO_REGEX.finditer(raw)]
        marker = None
        regex = None

        if polled_marker:
            marker = polled_marker
            regex = POLLED_REGEX
        elif auto_marker:
            marker = auto_marker
            regex = AUTO_REGEX

        # if we have found polled or autonomous record markers, work through the data...
        while marker:
            # for each record marker, set the start and stop points of the sample
            start = marker[0]
            if len(marker) > 1:
                # stopping point is the next record marker
                stop = marker[1]
            else:
                # stopping point is the end of the file
                stop = len(raw)

            # now create the initial sampling string
            sample = raw[start:stop]
            match = regex.match(sample)

            if match:
                # pull out of the initial sample string the DCL timestamps and a cleaned sample string
                collect_time = match.group(1)
                process_time = match.group(3)
 
                # required for sami rev k (stuff '*' ahead of group 4
                #cleaned = match.group(4) + match.group(5) + match.group(6)
                cleaned = '*' + match.group(4) + match.group(5) + match.group(6)

 
                # if we have a complete sample, process it.
                if len(cleaned) == 81:
                    # print '%s --- %s\n' % (timestamp, sample)
                    self._build_parsed_values(collect_time, process_time, cleaned)

            # bump to the next marker
            marker.pop(0)

    def _build_parsed_values(self, collect_time, process_time, sample):
        """
        Extract the data from the relevant regex groups and assign to elements
        of the data dictionary.
        """
        # Use the date_time_string from the collection time to calculate an
        # epoch timestamp (seconds since 1970-01-01), using that values as the
        # preferred time record for the data
        epts = dcl_to_epoch(collect_time)
        self.data.time.append(epts)
        self.data.collect_date_time.append(collect_time)
        self.data.process_date_time.append(process_time)

        self.data.unique_id.append(int(sample[1:3], 16))
        self.data.record_length.append(int(sample[3:5], 16))
        self.data.record_type.append(int(sample[5:7], 16))
        self.data.record_time.append(int(sample[7:15], 16))
        self.data.dark_reference_a.append(int(sample[15:19], 16))
        self.data.dark_signal_a.append(int(sample[19:23], 16))
        self.data.reference_434_a.append(int(sample[23:27], 16))
        self.data.signal_434_a.append(int(sample[27:31], 16))
        self.data.reference_620_a.append(int(sample[31:35], 16))
        self.data.signal_620_a.append(int(sample[35:39], 16))
        self.data.ratio_434.append(int(sample[39:43], 16))
        self.data.ratio_620.append(int(sample[43:47], 16))
        self.data.dark_reference_b.append(int(sample[47:51], 16))
        self.data.dark_signal_b.append(int(sample[51:55], 16))
        self.data.reference_434_b.append(int(sample[55:59], 16))
        self.data.signal_434_b.append(int(sample[59:63], 16))
        self.data.reference_620_b.append(int(sample[63:67], 16))
        self.data.signal_620_b.append(int(sample[67:71], 16))
        self.data.voltage_raw.append(int(sample[71:75], 16))
        self.data.thermistor_raw.append(int(sample[75:79], 16))


def main(argv=None):
    # load the input arguments
    args = inputs(argv)
    infile = os.path.abspath(args.infile)
    outfile = os.path.abspath(args.outfile)

    # initialize the Parser object for pco2w
    pco2w = Parser(infile)

    # load the data into a buffered object and parse the data into a dictionary
    pco2w.load_ascii()
    pco2w.parse_data()

    # write the resulting Bunch object via the toJSON method to a JSON
    # formatted data file (note, no pretty-printing keeping things compact)
    with open(outfile, 'w') as f:
        f.write(pco2w.data.toJSON())


if __name__ == '__main__':
    main()
