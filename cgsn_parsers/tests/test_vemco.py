#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.tests.test_parse_vemco
@file cgsn_parsers/tests/test_parse_vemco.py
@author Christopher Wingard
@brief Unit tests for parsing the raw Vemco VR2C status and tag detection data
"""
import numpy as np
import unittest

from nose.plugins.attrib import attr
from os import path

from cgsn_parsers.parsers.parse_vemco import Parser

# test data file recorded during driver development and bench top testing
TESTDATA = path.join(path.dirname(__file__), 'vemco/20240621.vemco.log')


@attr('parse')
class TestParsingUnit(unittest.TestCase):
    """
    OOI Endurance and Pioneer moorings use a custom-built system from WHOI to
    log data from a suite of instruments, including the Vemco VR2C acoustic
    receiver. The test data used below comes from a PI-funded project to
    deploy Vemco VR2C receivers as part of the OOI Endurance Array.
    """

    def setUp(self):
        """
        Load and parse the test vemco data and set the expected output array.
        """
        # initialize Parser object for the vemco using the test data file define above.
        self.vemco = Parser(TESTDATA)

        # set the expected output array minus the date/time strings
        self.expected_status = np.array([
            [450307, 52, 73, 68181, 12.2, 3.4, 47.5, 2.3, 11.5, 0.3, 2.9, -1.03, 0.16, -0.09],
            [450307, 57, 82, 68310, 12.2, 3.4, 47.5, 2.3, 11.5, 0.3, 2.9, -1.00, -0.06, -0.13],
            [450307, 67, 84, 68375, 12.0, 3.4, 47.5, 2.3, 11.0, 0.3, 2.9, -0.84, 0.25, 0.03],
            [450307, 70, 84, 68375, 12.2, 3.4, 47.5, 2.3, 11.2, 0.3, 2.9, -1.03, 0.28, 0.06]
        ])

        self.expected_detections = np.array([
            [450307, 53, 'A69-9001', '61461'],
            [450307, 54, 'A69-9001', '61461'],
            [450307, 55, 'A69-9001', '61461'],
            [450307, 56, 'A69-9001', '61461'],
            [450307, 58, 'A69-9001', '61461'],
            [450307, 59, 'A69-9001', '61461'],
            [450307, 60, 'A69-9001', '61461'],
            [450307, 61, 'A69-9001', '61461'],
            [450307, 62, 'A69-9001', '61461'],
            [450307, 63, 'A69-9001', '61461'],
            [450307, 64, 'A69-9001', '61461'],
            [450307, 65, 'A69-9001', '61461'],
            [450307, 66, 'A69-9001', '61461'],
            [450307, 68, 'A69-9001', '61461'],
            [450307, 69, 'A69-9001', '61461'],
        ])

    def test_parse_vemco(self):
        """
        Test parsing of the vemco data
        """
        self.vemco.load_vemco()
        self.vemco.parse_status()
        self.vemco.parse_tags()
        parsed = self.vemco.data.toDict()

        # check the status data
        np.testing.assert_array_equal(parsed['status']['serial_number'], self.expected_status[:, 0].astype(int))
        np.testing.assert_array_equal(parsed['status']['sequence'], self.expected_status[:, 1].astype(int))
        np.testing.assert_array_equal(parsed['status']['detection_count'], self.expected_status[:, 2].astype(float))
        np.testing.assert_array_equal(parsed['status']['ping_count'], self.expected_status[:, 3].astype(float))
        np.testing.assert_array_equal(parsed['status']['line_voltage'], self.expected_status[:, 4].astype(float))
        np.testing.assert_array_equal(parsed['status']['battery_voltage'], self.expected_status[:, 5].astype(float))
        np.testing.assert_array_equal(parsed['status']['battery_usage'], self.expected_status[:, 6].astype(float))
        np.testing.assert_array_equal(parsed['status']['current_consumption'], self.expected_status[:, 7].astype(float))
        np.testing.assert_array_equal(parsed['status']['internal_temperature'], self.expected_status[:, 8].astype(float))
        np.testing.assert_array_equal(parsed['status']['detection_memory_usage'], self.expected_status[:, 9].astype(float))
        np.testing.assert_array_equal(parsed['status']['raw_memory_usage'], self.expected_status[:, 10].astype(float))
        np.testing.assert_array_equal(parsed['status']['tilt_x'], self.expected_status[:, 11].astype(float))
        np.testing.assert_array_equal(parsed['status']['tilt_y'], self.expected_status[:, 12].astype(float))
        np.testing.assert_array_equal(parsed['status']['tilt_z'], self.expected_status[:, 13].astype(float))

        # check the tag detection data
        np.testing.assert_array_equal(parsed['tags']['serial_number'], self.expected_detections[:, 0].astype(int))
        np.testing.assert_array_equal(parsed['tags']['sequence'], self.expected_detections[:, 1].astype(int))
        np.testing.assert_array_equal(parsed['tags']['code_space'], self.expected_detections[:, 2].astype(str))
        np.testing.assert_array_equal(parsed['tags']['tag_id'], self.expected_detections[:, 3].astype(str))


if __name__ == '__main__':
    unittest.main()
