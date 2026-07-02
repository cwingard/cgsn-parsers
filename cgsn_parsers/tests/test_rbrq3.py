#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.tests.test_parse_rbrq3
@file cgsn_parsers/tests/test_parse_rbrq3.py
@author Paul Whelan
@brief Unit tests for parsing the RBR Quartz3 instrument data
"""
import numpy as np
import json
import unittest

from munch import Munch
from os import path

from cgsn_parsers.parsers.parse_rbrq3 import Parser

# data sources for testing the parser
RAWDATA = path.join(path.dirname(__file__), 'rbrq3/20231107.rbrq3.log')
EXPECTED = path.join(path.dirname(__file__), 'rbrq3/expected-20231107-rbrq3.txt')

# data sources for testing the processing
#PARSED = path.join(path.dirname(__file__), 'optaa/20150809_075841.optaa_cspp.json')

class TestParsingUnit(unittest.TestCase):
    """
    OOI Pioneer MAB moorings use the RBR PRESF Quartz3 pressure sensor.
    This unit test will [TBD]
    """
    def setUp(self):
        """
        Using the sample data, initialize the Parser object with parsed RBRQ3
        data and set the expected output arrays.
        """
        # initialize Parser objects for the CTDBP types defined above.
        self.rbrq3 = Parser(RAWDATA)
        self.rbrq3.load_ascii()
        self.rbrq3.parse_data()
        
        # set the expected output array [TBD]
        self.expected = np.genfromtxt( EXPECTED, skip_header=5)

    def test_parse_rbrq3(self):
        """
        Test parsing of the RBR Quartz3 data file
        """
        #pass
        #serial_num = np.array(self.rbrq3.data.serial_number)
        rbrtemp = np.array(self.rbrq3.data.temperature_00)
        rbrpressure = np.array(self.rbrq3.data.pressure_00)

        np.testing.assert_array_equal(rbrtemp, self.expected[:, 1])
        np.testing.assert_array_equal(rbrpressure, self.expected[:, 2])


if __name__ == '__main__':       
    unittest.main()
