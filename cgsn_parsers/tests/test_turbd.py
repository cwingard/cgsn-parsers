#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.tests.test_parse_turbd
@file cgsn_parsers/tests/test_parse_turbd.py
@author Paul Whelan
@brief Unit tests for parsing the Seapoint Turbidity sensor data
"""
import numpy as np
import unittest

from nose.plugins.attrib import attr
from os import path

from cgsn_parsers.parsers.parse_turbd import Parser

# test data file from AS03CPSM NSIF resident Seapoint Turbidity sensor
TESTDATA = path.join( path.dirname( __file__ ), 'turbd/turbd.log' )


@attr('parse')
class TestParsingUnit( unittest.TestCase ):
    """
    OOI Endurance and Pioneer moorings use a custom built system from WHOI to
    log data from a suite of instruments, including a Seapoint Turbidyt sensor.
    The test data used below comes from the AS03CPSM deployment on 2/28/2023.
    """
    def setUp( self ):
        """
        Load and parse the test METBK data and set the expected output array.
        """
        # initialize Parser objects for the metbk types defined above.
        self.turbd = Parser( TESTDATA )

        # set the expected output array minus the date/time strings
        self.expected = np.array([
            [0.7749, "NTU"],
            [0.8139, "NTU"],
            [0.8010, "NTU"],
            [0.7700, "NTU"],
            [0.7329, "NTU"],
            [0.7712, "NTU"],
            [0.7448, "NTU"],
            [0.7768, "NTU"],
            [0.7746, "NTU"],
            [0.7683, "NTU"],
            [0.7634, "NTU"],
            [0.7543, "NTU"],
            [0.7551, "NTU"],
            [0.7370, "NTU"],
            [0.7241, "NTU"],
            [0.7514, "NTU"],
            [0.6652, "NTU"],
            [0.7214, "NTU"],
            [0.6989, "NTU"],
            [0.6850, "NTU"],
            [0.6640, "NTU"],
            [0.5920, "NTU"],
            [0.6245, "NTU"],
            [0.3085, "NTU"],
            [0.3039, "NTU"],
            [0.3059, "NTU"],
            [0.2766, "NTU"],
            [0.2907, "NTU"],
            [0.2868, "NTU"],
            [0.2922, "NTU"],
            [0.2907, "NTU"],
            [0.2944, "NTU"],
            [0.3110, "NTU"] ])

    def test_parse_turbd( self ):
        """
        Test parsing of the turbd data
        """
        self.turbd.load_ascii()
        self.turbd.parse_data()
        parsed = self.turbd.data.toDict()

        np.testing.assert_array_equal( parsed['raw_signal_turbidity'], (self.expected[:, 0]).astype(float) )
        np.testing.assert_array_equal( parsed['turbd_units'], self.expected[:, 1] )

if __name__ == '__main__':
    unittest.main()
