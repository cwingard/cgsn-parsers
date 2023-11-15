#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.tests.test_parse_ifcb_hdr
@file cgsn_parsers/tests/test_parse_ifcb_hdr.py
@author Paul Whelan
@brief Unit tests for parsing the McLean IFCB instrument data
"""
import numpy as np
import json
import unittest

from munch import Munch
from nose.plugins.attrib import attr
from os import path

from cgsn_parsers.parsers.parse_ifcb_hdr import Parser

# data sources for testing the parser
RAWDATA = path.join(path.dirname(__file__), 'ifcb/D20230222T174812_IFCB195.hdr')
EXPECTED = path.join(path.dirname(__file__), 'ifcb/D20230222T174812_IFCB195_hdr_expected.txt')

# data sources for testing the processing
#PARSED = path.join(path.dirname(__file__), 'optaa/20150809_075841.optaa_cspp.json')

@attr('parse')
class TestParsingUnit(unittest.TestCase):
    """
    OOI Pioneer MAB moorings use the McLean IFCB sensor.
    This unit test will verify that the IFCB .hdr file is correctly parsed
    """
    def setUp(self):
        """
        Using the sample data file, initialize the Parser object with parsed IFCB header
        data and set the expected output arrays.
        """
        # initialize Parser objects for the CTDBP types defined above.
        self.ifcb = Parser(RAWDATA)
        self.ifcb.load_ascii()
        self.ifcb.parse_data()
        
        # set the expected output dicionary
        with open( EXPECTED ) as f:
            expData = f.read()
        self.expected = json.loads( expData )
            
    def test_parse_ifcb_hdr(self):
        """
        Test parsing of the IFCB header data file
        """

        for key in self.expected:
            np.testing.assert_equal( self.expected[ key ], self.ifcb.data[ key ] )
       

if __name__ == '__main__':       
    unittest.main()
