#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.tests.test_parse_pwrsys
@file cgsn_parsers/tests/test_parse_pwrsys.py
@author Christopher Wingard
@brief Unit tests for parsing the 2 different types of power system data
"""
import numpy as np
import unittest

from nose.plugins.attrib import attr
from os import path

from cgsn_parsers.parsers.parse_pwrsys import Parser

# Test data files obtained from the raw data server at https://rawdata.oceanobservatories.org/files.

# Test data PSC - CE07SHSM/D00007/cg_data/pwrsys/20180330.pwrsys.log
# Expected data - 
TEST_DATA_PWRSYS_PSC = path.join(path.dirname(__file__), 'pwrsys/20180330.pwrsys.log')

# Test data MPEA - CE07SHSM/D00007/cg_data/cpm3/pwrsys/20180405.pwrsys.log
# Expected data -
TEST_DATA_PWRSYS_MPEA = path.join(path.dirname(__file__), 'pwrsys/20180405.pwrsys.log')


@attr('parse')
class TestParsingUnit(unittest.TestCase):
    """
    This test class will parse and compare the outputs from the two types of power systems to data loaded via the numpy
    genfromtxt function. A mapping of the columns in the raw files to the array indices in the expected data was created
    using Excel to look at the files and number/label the columns.
    """
    def setUp(self):
        """
        Using sample data files from above, initialize the Parser objects for each of the 3 pwrsys data output formats
        and setup the expected output arrays.
        """
        # Initialize Parser objects for the pwrsys types defined above.
        self.pwrsys_psc = Parser(TEST_DATA_PWRSYS_PSC, 'psc')
        self.pwrsys_mpea = Parser(TEST_DATA_PWRSYS_MPEA, 'mpea')

        # Set the expected output arrays for each of the pwrsys output formats. Import the data as strings, these
        # can then be compared to the data on a case-by-case basis per data type.
        self.psc_expected = np.genfromtxt(TEST_DATA_PWRSYS_PSC, dtype=str, delimiter=' ')
        self.mpea_expected = np.genfromtxt(TEST_DATA_PWRSYS_MPEA, dtype=str, delimiter=' ')

    def test_parse_pwrsys_psc(self):
        """
        Compare the Power System Controller (PSC) data parsed into a JSON object with the same data pulled in via the
        numpy genfromtxt method.
        """
        self.pwrsys_psc.load_ascii()
        self.pwrsys_psc.parse_data()
        parsed = self.pwrsys_psc.data.toDict()

        np.testing.assert_array_equal(parsed['main_voltage'], (self.psc_expected[:, 4]).astype(float))
        np.testing.assert_array_equal(parsed['main_current'], (self.psc_expected[:, 5]).astype(float))
        np.testing.assert_array_equal(parsed['percent_charge'], (self.psc_expected[:, 6]).astype(float))
        np.testing.assert_array_equal(parsed['override_flag'], [int(i, 16) for i in self.psc_expected[:, 7]])
        np.testing.assert_array_equal(parsed['error_flag1'], [int(i, 16) for i in self.psc_expected[:, 8]])
        np.testing.assert_array_equal(parsed['error_flag2'], [int(i, 16) for i in self.psc_expected[:, 9]])
        np.testing.assert_array_equal(parsed['solar_panel1_state'], (self.psc_expected[:, 11]).astype(int))
        np.testing.assert_array_equal(parsed['solar_panel1_voltage'], (self.psc_expected[:, 12]).astype(float))
        np.testing.assert_array_equal(parsed['solar_panel1_current'], (self.psc_expected[:, 13]).astype(float))
        np.testing.assert_array_equal(parsed['solar_panel2_state'], (self.psc_expected[:, 15]).astype(int))
        np.testing.assert_array_equal(parsed['solar_panel2_voltage'], (self.psc_expected[:, 16]).astype(float))
        np.testing.assert_array_equal(parsed['solar_panel2_current'], (self.psc_expected[:, 17]).astype(float))
        np.testing.assert_array_equal(parsed['solar_panel3_state'], (self.psc_expected[:, 19]).astype(int))
        np.testing.assert_array_equal(parsed['solar_panel3_voltage'], (self.psc_expected[:, 20]).astype(float))
        np.testing.assert_array_equal(parsed['solar_panel3_current'], (self.psc_expected[:, 21]).astype(float))
        np.testing.assert_array_equal(parsed['solar_panel4_state'], (self.psc_expected[:, 23]).astype(int))
        np.testing.assert_array_equal(parsed['solar_panel4_voltage'], (self.psc_expected[:, 24]).astype(float))
        np.testing.assert_array_equal(parsed['solar_panel4_current'], (self.psc_expected[:, 25]).astype(float))
        np.testing.assert_array_equal(parsed['wind_turbine1_state'], (self.psc_expected[:, 27]).astype(int))
        np.testing.assert_array_equal(parsed['wind_turbine1_voltage'], (self.psc_expected[:, 28]).astype(float))
        np.testing.assert_array_equal(parsed['wind_turbine1_current'], (self.psc_expected[:, 29]).astype(float))
        np.testing.assert_array_equal(parsed['wind_turbine2_state'], (self.psc_expected[:, 31]).astype(int))
        np.testing.assert_array_equal(parsed['wind_turbine2_voltage'], (self.psc_expected[:, 32]).astype(float))
        np.testing.assert_array_equal(parsed['wind_turbine2_current'], (self.psc_expected[:, 33]).astype(float))
        np.testing.assert_array_equal(parsed['battery_bank1_temperature'], (self.psc_expected[:, 43]).astype(float))
        np.testing.assert_array_equal(parsed['battery_bank1_voltage'], (self.psc_expected[:, 44]).astype(float))
        np.testing.assert_array_equal(parsed['battery_bank1_current'], (self.psc_expected[:, 45]).astype(float))
        np.testing.assert_array_equal(parsed['battery_bank2_temperature'], (self.psc_expected[:, 47]).astype(float))
        np.testing.assert_array_equal(parsed['battery_bank2_voltage'], (self.psc_expected[:, 48]).astype(float))
        np.testing.assert_array_equal(parsed['battery_bank2_current'], (self.psc_expected[:, 49]).astype(float))
        np.testing.assert_array_equal(parsed['battery_bank3_temperature'], (self.psc_expected[:, 51]).astype(float))
        np.testing.assert_array_equal(parsed['battery_bank3_voltage'], (self.psc_expected[:, 52]).astype(float))
        np.testing.assert_array_equal(parsed['battery_bank3_current'], (self.psc_expected[:, 53]).astype(float))
        np.testing.assert_array_equal(parsed['battery_bank4_temperature'], (self.psc_expected[:, 55]).astype(float))
        np.testing.assert_array_equal(parsed['battery_bank4_voltage'], (self.psc_expected[:, 56]).astype(float))
        np.testing.assert_array_equal(parsed['battery_bank4_current'], (self.psc_expected[:, 57]).astype(float))
        np.testing.assert_array_equal(parsed['external_voltage'], (self.psc_expected[:, 59]).astype(float))
        np.testing.assert_array_equal(parsed['external_current'], (self.psc_expected[:, 60]).astype(float))
        np.testing.assert_array_equal(parsed['internal_voltage'], (self.psc_expected[:, 62]).astype(float))
        np.testing.assert_array_equal(parsed['internal_current'], (self.psc_expected[:, 63]).astype(float))
        np.testing.assert_array_equal(parsed['internal_temperature'], (self.psc_expected[:, 64]).astype(float))
        np.testing.assert_array_equal(parsed['seawater_ground_state'], (self.psc_expected[:, 68]).astype(int))
        np.testing.assert_array_equal(parsed['seawater_ground_positve'], (self.psc_expected[:, 69]).astype(float))
        np.testing.assert_array_equal(parsed['seawater_ground_negative'], (self.psc_expected[:, 70]).astype(float))
        np.testing.assert_array_equal(parsed['cvt_state'], (self.psc_expected[:, 72]).astype(int))
        np.testing.assert_array_equal(parsed['cvt_voltage'], (self.psc_expected[:,73]).astype(float))
        np.testing.assert_array_equal(parsed['cvt_current'], (self.psc_expected[:, 74]).astype(float))
        np.testing.assert_array_equal(parsed['cvt_interlock'], (self.psc_expected[:, 75]).astype(int))
        np.testing.assert_array_equal(parsed['cvt_temperature'], (self.psc_expected[:, 76]).astype(float))
        np.testing.assert_array_equal(parsed['error_flag3'], [int(i, 16) for i in self.psc_expected[:, 77]])

    def test_parse_pwrsys_mpea(self):
        """
        Compare the MFN Power and ?? Adapter (MPEA) data parsed into a JSON object with the same data pulled in via the
        numpy genfromtxt method.
        """
        self.pwrsys_mpea.load_ascii()
        self.pwrsys_mpea.parse_data()
        parsed = self.pwrsys_mpea.data.toDict()

        np.testing.assert_array_equal(parsed['main_voltage'], (self.mpea_expected[:, 4]).astype(float))
        np.testing.assert_array_equal(parsed['main_current'], (self.mpea_expected[:, 5]).astype(float))
        np.testing.assert_array_equal(parsed['error_flag1'], [int(i, 16) for i in self.mpea_expected[:, 6]])
        np.testing.assert_array_equal(parsed['error_flag2'], [int(i, 16) for i in self.mpea_expected[:, 7]])
        np.testing.assert_array_equal(parsed['cv1_state'], (self.mpea_expected[:, 9]).astype(int))
        np.testing.assert_array_equal(parsed['cv1_voltage'], (self.mpea_expected[:, 10]).astype(float))
        np.testing.assert_array_equal(parsed['cv1_current'], (self.mpea_expected[:, 11]).astype(float))
        np.testing.assert_array_equal(parsed['cv2_state'], (self.mpea_expected[:, 13]).astype(int))
        np.testing.assert_array_equal(parsed['cv2_voltage'], (self.mpea_expected[:, 14]).astype(float))
        np.testing.assert_array_equal(parsed['cv2_current'], (self.mpea_expected[:, 15]).astype(float))
        np.testing.assert_array_equal(parsed['cv3_state'], (self.mpea_expected[:, 17]).astype(int))
        np.testing.assert_array_equal(parsed['cv3_voltage'], (self.mpea_expected[:, 18]).astype(float))
        np.testing.assert_array_equal(parsed['cv3_current'], (self.mpea_expected[:, 19]).astype(float))
        np.testing.assert_array_equal(parsed['cv4_state'], (self.mpea_expected[:, 21]).astype(int))
        np.testing.assert_array_equal(parsed['cv4_voltage'], (self.mpea_expected[:, 22]).astype(float))
        np.testing.assert_array_equal(parsed['cv4_current'], (self.mpea_expected[:, 23]).astype(float))
        np.testing.assert_array_equal(parsed['cv5_state'], (self.mpea_expected[:, 25]).astype(int))
        np.testing.assert_array_equal(parsed['cv5_voltage'], (self.mpea_expected[:, 26]).astype(float))
        np.testing.assert_array_equal(parsed['cv5_current'], (self.mpea_expected[:, 27]).astype(float))
        np.testing.assert_array_equal(parsed['cv6_state'], (self.mpea_expected[:, 29]).astype(int))
        np.testing.assert_array_equal(parsed['cv6_voltage'], (self.mpea_expected[:, 30]).astype(float))
        np.testing.assert_array_equal(parsed['cv6_current'], (self.mpea_expected[:, 31]).astype(float))
        np.testing.assert_array_equal(parsed['cv7_state'], (self.mpea_expected[:, 33]).astype(int))
        np.testing.assert_array_equal(parsed['cv7_voltage'], (self.mpea_expected[:, 34]).astype(float))
        np.testing.assert_array_equal(parsed['cv7_current'], (self.mpea_expected[:, 35]).astype(float))
        np.testing.assert_array_equal(parsed['auxiliary_state'], (self.mpea_expected[:, 37]).astype(int))
        np.testing.assert_array_equal(parsed['auxiliary_voltage'], (self.mpea_expected[:, 38]).astype(float))
        np.testing.assert_array_equal(parsed['auxiliary_current'], (self.mpea_expected[:, 39]).astype(float))
        np.testing.assert_array_equal(parsed['hotel_5v_voltage'], (self.mpea_expected[:, 41]).astype(float))
        np.testing.assert_array_equal(parsed['hotel_5v_current'], (self.mpea_expected[:, 42]).astype(float))
        np.testing.assert_array_equal(parsed['temperature'], (self.mpea_expected[:, 43]).astype(float))
        np.testing.assert_array_equal(parsed['relative_humidity'], (self.mpea_expected[:, 44]).astype(float))
        np.testing.assert_array_equal(parsed['leak_detect'], (self.mpea_expected[:, 45]).astype(float))
        np.testing.assert_array_equal(parsed['internal_pressure'], (self.mpea_expected[:, 46]).astype(float))


if __name__ == '__main__':
    unittest.main()
