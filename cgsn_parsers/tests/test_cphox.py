#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.tests.test_parse_cphox
@file cgsn_parsers/tests/test_parse_cphox.py
@author Christopher Wingard
@brief Unit tests for parsing the raw Sea-Bird Scientific Deep SeapHOx (CPHOX)
    sensor data.
"""
import numpy as np
import unittest

from nose.plugins.attrib import attr
from os import path

from cgsn_parsers.parsers.parse_cphox import Parser

# test data file recorded during a Spring 2024 test deployment of the CPHOX
TESTDATA = path.join(path.dirname(__file__), 'cphox/20240810.cphox.log')


@attr('parse')
class TestParsingUnit(unittest.TestCase):
    """
    OOI Endurance and Pioneer moorings use a custom-built system from WHOI to
    log data from a suite of instruments, including the Sea-Bird Scientific
    Deep SeapHOx (CPHOX) sensor. The CPHOX sensor measures pH, dissolved
    oxygen, temperature, salinity, and other parameters.
    """

    def setUp(self):
        """
        Load and parse the test cphox data and set the expected output array.
        """
        # initialize Parser object for the cphox using the test data file define above.
        self.cphox = Parser(TESTDATA)

        # set the expected output array minus the date/time strings
        self.expected = np.array([
            [2056, 11937, 0, 9.4181, 7.8097, -0.993480, 7.100, 33.1319, 3.57378, 4.215, 0.0, 9.7],
            [2056, 11945, 0, 9.8234, 7.8524, -0.990788, 7.421, 33.1955, 3.61651, 4.700, 0.0, 9.7],
            [2056, 11953, 0, 10.0437, 7.9092, -0.987434, 6.862, 33.2203, 3.63884, 5.265, 0.0, 10.0],
            [2056, 11961, 0, 10.8670, 8.0533, -0.978541, 6.936, 33.1521, 3.70677, 6.754, 0.1, 11.2],
            [2056, 11969, 0, 10.5995, 7.9649, -0.983680, 7.181, 33.0592, 3.67319, 5.831, 0.1, 10.8],
            [2056, 11977, 0, 10.9032, 8.0020, -0.981413, 7.072, 33.1704, 3.71191, 6.210, 0.1, 11.1],
            [2056, 11985, 0, 10.4348, 7.9350, -0.985554, 7.182, 33.1168, 3.66403, 5.512, 0.1, 10.7],
            [2056, 11993, 0, 10.4440, 7.8808, -0.988597, 7.060, 33.1116, 3.66433, 4.978, 0.0, 10.5],
            [2056, 12001, 0, 10.0179, 7.8618, -0.989986, 7.279, 33.0582, 3.62057, 4.674, 0.0, 10.3],
            [2056, 12009, 0, 10.7256, 7.9690, -0.983403, 7.162, 33.1391, 3.69262, 5.715, 0.2, 11.2],
            [2056, 12017, 0, 9.7040, 7.8576, -0.990249, 7.069, 32.7665, 3.56378, 4.603, 0.0, 10.3],
            [2056, 12025, 0, 9.7243, 7.7569, -0.995787, 7.386, 32.6505, 3.55424, 3.860, 0.0, 9.3],
        ])

    def test_parse_cphox(self):
        """
        Test parsing of the cphox data
        """
        self.cphox.load_ascii()
        self.cphox.parse_data()
        parsed = self.cphox.data.toDict()

        # check the parsed data against the expected output
        np.testing.assert_array_equal(parsed['serial_number'].astype(int), self.expected[:, 0])
        np.testing.assert_array_equal(parsed['sample_number'], self.expected[:, 1])
        np.testing.assert_array_equal(parsed['error_flag'], self.expected[:, 2])
        np.testing.assert_array_equal(parsed['temperature'], self.expected[:, 3])
        np.testing.assert_array_equal(parsed['seawater_ph'], self.expected[:, 4])
        np.testing.assert_array_equal(parsed['external_reference'], self.expected[:, 5])
        np.testing.assert_array_equal(parsed['pressure'], self.expected[:, 6])
        np.testing.assert_array_equal(parsed['salinity'], self.expected[:, 7])
        np.testing.assert_array_equal(parsed['conductivity'], self.expected[:, 8])
        np.testing.assert_array_equal(parsed['oxygen_concentration'], self.expected[:, 9])
        np.testing.assert_array_equal(parsed['internal_humidity'], self.expected[:, 10])
        np.testing.assert_array_equal(parsed['internal_temperature'], self.expected[:, 11])


if __name__ == '__main__':
    unittest.main()
