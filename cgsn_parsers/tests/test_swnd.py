#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.tests.test_parse_swnd
@file cgsn_parsers/tests/test_parse_swnd.py
@author Christopher Wingard
@brief Unit tests for parsing the raw ASIMET Sonic Wind module data
"""
import numpy as np
import unittest

from nose.plugins.attrib import attr
from os import path

from cgsn_parsers.parsers.parse_swnd import Parser

# test data file recorded during driver development and bench top testing
TESTDATA = path.join(path.dirname(__file__), 'swnd/20240122.metwnd.log')


@attr('parse')
class TestParsingUnit(unittest.TestCase):
    """
    OOI Endurance and Pioneer moorings use a custom-built system from WHOI to
    log data from a suite of instruments, including the Sonic Wind (SWND)
    module. The test data used below comes from bench top testing of the SWND
    module on 1/22/2024.
    """
    def setUp(self):
        """
        Load and parse the test SWND data and set the expected output array.
        """
        # initialize Parser object for the SWND using the test data file define above.
        self.swnd = Parser(TESTDATA)

        # set the expected output array minus the date/time strings
        self.expected = np.array([
            [0.00, -0.01, 344.47, 21.44, 78.3, 1.0, -0.2],
            [0.00, 0.00, 344.45, 21.40, 78.2, 0.9, -0.2],
            [0.02, -0.01, 344.47, 21.44, 78.4, 0.9, -0.1],
            [0.02, -0.01, 344.47, 21.44, 78.4, 0.9, -0.1],
            [0.00, -0.03, 344.39, 21.30, 77.6, 1.0, -0.2],
            [-0.01, -0.03, 344.47, 21.44, 77.7, 1.0, -0.2],
            [-0.01, -0.02, 344.39, 21.30, 77.5, 1.0, -0.2],
            [0.00, -0.02, 344.31, 21.16, 77.7, 1.0, -0.2],
        ])

    def test_parse_swnd(self):
        """
        Test parsing of the swnd data
        """
        self.swnd.load_ascii()
        self.swnd.parse_data()
        parsed = self.swnd.data.toDict()

        np.testing.assert_array_equal(parsed['u_axis_wind_speed'], (self.expected[:, 0]).astype(float))
        np.testing.assert_array_equal(parsed['v_axis_wind_speed'], (self.expected[:, 1]).astype(float))
        np.testing.assert_array_equal(parsed['speed_of_sound'], (self.expected[:, 2]).astype(float))
        np.testing.assert_array_equal(parsed['sonic_temperature'], (self.expected[:, 3]).astype(float))
        np.testing.assert_array_equal(parsed['heading'], (self.expected[:, 4]).astype(float))
        np.testing.assert_array_equal(parsed['pitch'], (self.expected[:, 5]).astype(float))
        np.testing.assert_array_equal(parsed['roll'], (self.expected[:, 6]).astype(float))


if __name__ == '__main__':
    unittest.main()
