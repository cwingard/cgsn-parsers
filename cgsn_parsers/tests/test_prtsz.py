#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.tests.test_parse_prtsz
@file cgsn_parsers/tests/test_parse_prtsz.py
@author Samuel Dahlberg
@brief Unit tests for parsing the PRTSZ instrument data
"""
import numpy as np
import unittest

from nose.plugins.attrib import attr
from os import path

from cgsn_parsers.parsers.parse_prtsz import Parser

# data sources for testing the parser
RAWDATA = path.join(path.dirname(__file__), 'prtsz/prtsz.log')
EXPECTED = path.join(path.dirname(__file__), 'prtsz/prtsz_expected.txt')


@attr('parse')
class TestParsingUnit(unittest.TestCase):
    """
    This unit test will parse sample log code derived from the PRTSZ Logger, and check key
    data outputs as well as select engineer data to validate the output variables.
    """
    def setUp(self):
        """
        Using the sample data, initialize the Parser object with parsed PRTSZ
        data and set the expected output arrays.
        """
        # initialize Parser objects.
        self.prtsz = Parser(RAWDATA)
        self.prtsz.load_ascii()
        self.prtsz.parse_data()

        # set the expected output array.
        self.expected = np.genfromtxt(EXPECTED, delimiter=",")

    def test_parse_prtsz(self):
        """
        Test parsing of the PRTSZ data file. Choosing random data columns to verify.
        """
        prtsz_concentration = np.array(self.prtsz.data.volume_concentration)
        mean_diameter = np.array(self.prtsz.data.mean_diameter)
        pressure = np.array(self.prtsz.data.pressure)

        np.testing.assert_array_equal(prtsz_concentration[0, :], self.expected[1:37])
        np.testing.assert_array_equal(mean_diameter, self.expected[43])
        np.testing.assert_array_equal(pressure, self.expected[46])


if __name__ == '__main__':
    unittest.main()
