#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.tests.test_mmp_prawler
@file cgsn_parsers/tests/test_mmp_prawler.py
@author Christopher Wingard
@brief Unit tests for parsing the McLane Prawler MMP mixed binary/ASCII data files.
"""
import unittest

from os import path

from cgsn_parsers.parsers.parse_mmp_prawler import Parser

TESTDATA = path.join(path.dirname(__file__), 'prawler/prkt_20240416_050026.DAT')
TESTDATA_FLORT = path.join(path.dirname(__file__), 'prawler/prkt_20240416_050026_flort.DAT')


class TestParsingUnit(unittest.TestCase):
    """
    OOI Shallow Water Profiler moorings use a McLane Prawler MMP profiler, telemetered via the STC system as
    mixed binary/ASCII record blocks (engineering, science profile, and station list data).

    The engineering and science data values checked here are a regression baseline captured from the parser's
    own output against the sample files -- the byte layout is documented in ParameterNames in
    parse_mmp_prawler.py, but wasn't independently re-derived byte-by-byte here. The file summary header values
    are independently verified against the raw ASCII header text in the fixture.
    """
    def setUp(self):
        """
        Using the sample data file, initialize the Parser object and parse the data.
        """
        self.prawler = Parser(TESTDATA)
        self.prawler.load_binary()
        self.prawler.parse_prawler()

    def test_parse_summary(self):
        """
        Test parsing of the ASCII file summary header.
        """
        summary = self.prawler.data.summarydata
        self.assertEqual(summary.datetime[0], '20240416 050026')
        self.assertEqual(summary.ID[0], '01')
        self.assertEqual(summary.serial_number[0], '70012693')
        self.assertEqual(summary.voltage[0], '8.80')
        self.assertEqual(summary.records[0], '8')
        self.assertEqual(summary.length[0], '6724')
        self.assertEqual(summary.events[0], '863')

    def test_parse_engineering(self):
        """
        Test parsing of the first two binary engineering data records.
        """
        eng = self.prawler.data.engdata
        self.assertEqual(len(eng.depth), 84)
        self.assertEqual(eng.depth[:2], [2, 16])
        self.assertEqual(eng.direction[:2], [2, 1])
        self.assertEqual(eng.profile_count[:2], [24, 24])
        self.assertEqual(eng.sample_rate[:2], [4, 4])
        self.assertEqual(eng.vacuum_level[:2], [992, 1014])
        self.assertEqual(eng.water_detect[:2], ['0', '0'])
        self.assertEqual(eng.prawler_mode[:2], ['0', '0'])
        self.assertEqual(eng.calibration[:2], ['1', '1'])

    def test_parse_science(self):
        """
        Test parsing of the first three binary science profile data records (no fluorometer channel present
        on this unit).
        """
        sci = self.prawler.data.scidata
        self.assertEqual(len(sci.epoch_time), 83)
        self.assertEqual(sci.epoch_time[:3], [1713229481, 1713229487, 1713229493])
        self.assertEqual(sci.pressure[:3], [2.16, 2.39, 2.72])
        self.assertEqual(sci.temperature[:3], [13.5, 13.562, 13.546])
        self.assertEqual(sci.conductivity[:3], [3.5269, 3.5337000000000005, 3.5351])
        self.assertEqual(sci.optode_temperature[:3], [32.969, 32.891, 32.912])
        self.assertEqual(sci.optode_dissolved_oxygen[:3], [13.512, 13.569, 13.581])
        self.assertEqual(sci.flu_beta_count[:3], [0.0, 0.0, 0.0])

    def test_parse_science_with_flort(self):
        """
        Test parsing of a unit variant that includes the optional fluorometer channel in its science profile
        records.
        """
        prawler = Parser(TESTDATA_FLORT)
        prawler.load_binary()
        prawler.parse_prawler()
        sci = prawler.data.scidata

        self.assertEqual(len(sci.epoch_time), 10)
        self.assertEqual(sci.epoch_time[:3], [1727676032, 1727676040, 1727676048])
        self.assertEqual(sci.flu_beta_count[:3], [231.0, 2.0, 256.0])
        self.assertEqual(sci.flu_chl_count[:3], [51.0, 51.0, 49.0])
        self.assertEqual(sci.flu_cdom_count[:3], [64.0, 64.0, 65.0])


if __name__ == '__main__':
    unittest.main()
