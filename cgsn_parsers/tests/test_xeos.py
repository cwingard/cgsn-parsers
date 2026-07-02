#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.tests.test_xeos
@file cgsn_parsers/tests/test_xeos.py
@author Christopher Wingard
@brief Unit tests for parsing the Xeos beacon email data, covering both the legacy (kilo/melo) and Rover-X/
    Apollo-X beacon message formats.
"""
import unittest

from os import path

from cgsn_parsers.parsers.parse_xeos import Parser

TESTDATA_LEGACY = path.join(path.dirname(__file__), 'xeos/300434062570040.log')
TESTDATA_XPOS = path.join(path.dirname(__file__), 'xeos/xeos_x_with_extra_info.txt')


class TestParsingUnit(unittest.TestCase):
    """
    OOI surface moorings use Xeos Iridium beacons for position reporting and watch circle monitoring. Legacy
    (kilo/melo) beacons and the newer Rover-X/Apollo-X beacons use different message formats, handled by two
    separate regex patterns in the parser.
    """
    def test_parse_xeos_legacy(self):
        """
        Test parsing of legacy beacon position records, using the 'ALARM' and 'OK' watch-circle message
        variants (MOMSN 1733 and 1897 respectively) from the sample file. Note the sample file contains no
        example of the third ('no watch circle configured') message variant.
        """
        xeos = Parser(TESTDATA_LEGACY, surface=1, last_read=0)
        xeos.load_ascii()
        xeos.parse_data()
        data = xeos.data

        i_alarm = data.momsn.index(1733)
        i_ok = data.momsn.index(1897)

        self.assertEqual(data.transfer_status[i_alarm], 1)
        self.assertEqual(data.estimated_latitude[i_alarm], 35.94222)
        self.assertEqual(data.estimated_longitude[i_alarm], -75.10288)
        self.assertEqual(data.cep_radius[i_alarm], 10)
        self.assertEqual(data.watch_circle_status[i_alarm], 2)
        self.assertEqual(data.latitude_xeos[i_alarm], 35.94994)
        self.assertEqual(data.longitude_xeos[i_alarm], -75.11924)
        self.assertEqual(data.distance_from_center[i_alarm], 2320)
        self.assertAlmostEqual(data.time_in_circle[i_alarm], 0.0)
        self.assertEqual(data.signal_strength[i_alarm], 43)
        self.assertAlmostEqual(data.battery_voltage[i_alarm], 15.57)
        self.assertEqual(data.subsurface_beacon[i_alarm], 1)

        self.assertEqual(data.transfer_status[i_ok], 1)
        self.assertEqual(data.watch_circle_status[i_ok], 1)
        self.assertEqual(data.latitude_xeos[i_ok], 35.95014)
        self.assertEqual(data.longitude_xeos[i_ok], -75.11986)
        self.assertEqual(data.distance_from_center[i_ok], 4)
        self.assertAlmostEqual(data.time_in_circle[i_ok], 121.0)
        self.assertEqual(data.signal_strength[i_ok], 42)
        self.assertAlmostEqual(data.battery_voltage[i_ok], 15.69)

    def test_parse_xeos_xpos(self):
        """
        Test parsing of Rover-X/Apollo-X format beacon position records.
        """
        xeos = Parser(TESTDATA_XPOS, surface=0, last_read=0)
        xeos.load_ascii()
        xeos.parse_data()
        data = xeos.data

        self.assertEqual(len(data.momsn), 27)

        self.assertEqual(data.momsn[0], 316)
        self.assertEqual(data.time[0], 1721433631)
        self.assertEqual(data.transfer_status[0], 1)
        self.assertEqual(data.estimated_latitude[0], 44.64401)
        self.assertEqual(data.estimated_longitude[0], -124.30583)
        self.assertEqual(data.cep_radius[0], 9)
        self.assertEqual(data.battery_voltage[0], 13.61)
        self.assertEqual(data.loaded_voltage[0], 11.85)
        self.assertEqual(data.sched_timer[0], 0)
        self.assertEqual(data.watch_circle_status[0], 0)
        self.assertEqual(data.latitude_xeos[0], 44.6348233)
        self.assertEqual(data.longitude_xeos[0], -124.3033283)
        self.assertEqual(data.altitude[0], 37.0)
        self.assertEqual(data.signal_strength[0], 49)
        self.assertEqual(data.num_satellites[0], 5)
        self.assertEqual(data.bearing[0], 146.5)
        self.assertEqual(data.measurement_speed[0], 5.09)
        self.assertEqual(data.time_to_fix[0], 31)
        self.assertEqual(data.highest_hdop[0], 17.6)
        self.assertEqual(data.subsurface_beacon[0], 0)

        self.assertEqual(data.momsn[1], 317)
        self.assertEqual(data.time[1], 1721520003)
        self.assertEqual(data.estimated_latitude[1], 44.62311)
        self.assertEqual(data.estimated_longitude[1], -124.27741)
        self.assertEqual(data.cep_radius[1], 2)
        self.assertEqual(data.battery_voltage[1], 13.61)
        self.assertEqual(data.loaded_voltage[1], 11.55)
        self.assertEqual(data.latitude_xeos[1], 44.6348683)
        self.assertEqual(data.longitude_xeos[1], -124.3037432)
        self.assertEqual(data.altitude[1], 80.0)
        self.assertEqual(data.signal_strength[1], 45)
        self.assertEqual(data.num_satellites[1], 4)
        self.assertEqual(data.bearing[1], 326.6)
        self.assertEqual(data.measurement_speed[1], 9.69)
        self.assertEqual(data.time_to_fix[1], 3)
        self.assertEqual(data.highest_hdop[1], 24.3)


if __name__ == '__main__':
    unittest.main()
