#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.tests.test_parse_nutnr
@file cgsn_parsers/tests/test_parse_nutnr.py
@author Christopher Wingard
@brief Unit tests for parsing the 3 different types of NUTNR data
"""
import numpy as np
import unittest

from nose.plugins.attrib import attr
from os import path

from cgsn_parsers.parsers.parse_nutnr import Parser

# Test data files obtained from the raw data server at https://rawdata.oceanobservatories.org/files.

# Test data - CE01ISSM/D00003/dcl16/nutnr/20150616.nutnr.log
# Expected data - CE01ISSM/R00003/instrmts/dcl16/NUTNR_sn264/ce01issm_nutnr_264_recovered_2015-10-23/SCH15168.DAT
TEST_DATA_NUTNR_COND = path.join(path.dirname(__file__), 'nutnr/20150616.nutnr.log')
EXPECTED_DATA_NUTNR_COND = path.join(path.dirname(__file__), 'nutnr/SCH15167.DAT')

# Test data - CE02SHSM/D00005/cg_data/dcl26/nutnr/20170427.nutnr.log
# Expected data - CE02SHSM/R00005/instrmts/dcl26/NUTNR_sn287/ce02shsm_nutnr_287_recovered_2017-11-03/SCH17117.DAT
TEST_DATA_NUTNR_ISUS = path.join(path.dirname(__file__), 'nutnr/20170427.nutnr.log')
EXPECTED_DATA_NUTNR_ISUS = path.join(path.dirname(__file__), 'nutnr/SCH17117.DAT')

# Test data - CE01ISSM/D00008/cg_data/dcl16/nutnr/20171020.nutnr.log
# Expected data - CE01ISSM/R00008/instrmts/dcl16/NUTNR_sn1056/ce01issm_nutnr_1056_recovered_2018-04-01/DAT/D2017293.CSV
TEST_DATA_NUTNR_SUNA = path.join(path.dirname(__file__), 'nutnr/20171020.nutnr.log')
EXPECTED_DATA_NUTNR_SUNA = path.join(path.dirname(__file__), 'nutnr/D2017293.CSV')


@attr('parse')
class TestParsingUnit(unittest.TestCase):
    """
    OOI Endurance, Global and Pioneer moorings use the Sea-Bird Scientific (formerly Satlantic) nitrate sensors to
    measure the concentration of nitrate near the surface and at 7 m water depth. Formerly we were using the ISUS
    sensor (configured to output either full ASCII frames or condensed ASCII frames). We have now switched to using
    the newer SUNA model, outputting only the full ASCII frames.

    This test class will parse and compare the outputs from all three types of NUTNRs to recovered instrument data to
    confirm the parser functions as expected.
    """
    def setUp(self):
        """
        Using sample data files from above, initialize the Parser objects for each of the 3 NUTNR data output formats
        and setup the expected output arrays.
        """

        # Initialize Parser objects for the NUTNR types defined above.
        self.nutnr_cond = Parser(TEST_DATA_NUTNR_COND, 'isus_condensed')
        self.nutnr_isus = Parser(TEST_DATA_NUTNR_ISUS, 'isus')
        self.nutnr_suna = Parser(TEST_DATA_NUTNR_SUNA, 'suna')

        # Set the expected output arrays for the each of the NUTNR output formats.
        data = np.genfromtxt(EXPECTED_DATA_NUTNR_COND, skip_header=12, delimiter=',')
        fr, _ = np.modf(data[:, 2])  # return fractional part of decimal hours time stamp
        n = fr >= 0.5   # setup boolean indices for samples collected at the bottom of the hour (>= 0.5)
        self.cond_expected = data[n, :]  # keep expected data collected only at the bottom of the hour
        self.isus_expected = np.genfromtxt(EXPECTED_DATA_NUTNR_ISUS, skip_header=12, delimiter=',')
        self.suna_expected = np.genfromtxt(EXPECTED_DATA_NUTNR_SUNA, skip_header=14, delimiter=',')

    def test_parse_nutnr_cond(self):
        """
        Test parsing of an ISUS outputting condensed ASCII frames as recorded by the DCL versus recovered instrument
        data loaded from a CSV file per basic processing from above
        """
        self.nutnr_cond.load_ascii()
        self.nutnr_cond.parse_data()
        parsed = self.nutnr_cond.data.toDict()

        np.testing.assert_array_equal(parsed['decimal_hours'], self.cond_expected[:, 2])
        np.testing.assert_array_equal(parsed['nitrate_concentration'], self.cond_expected[:, 3])
        np.testing.assert_array_equal(parsed['auxiliary_fit_1st'], self.cond_expected[:, 4])
        np.testing.assert_array_equal(parsed['auxiliary_fit_2nd'], self.cond_expected[:, 5])
        np.testing.assert_array_equal(parsed['auxiliary_fit_3rd'], self.cond_expected[:, 6])
        np.testing.assert_array_equal(parsed['rms_error'], self.cond_expected[:, 7])

    def test_parse_nutnr_isus(self):
        """
        Test parsing of an ISUS outputting full ASCII frames as recorded by the DCL versus recovered instrument
        data loaded from a CSV file per basic processing from above
        """
        self.nutnr_isus.load_ascii()
        self.nutnr_isus.parse_data()
        parsed = self.nutnr_isus.data.toDict()

        np.testing.assert_array_equal(parsed['decimal_hours'], self.isus_expected[:, 2])
        np.testing.assert_array_equal(parsed['nitrate_concentration'], self.isus_expected[:, 3])
        np.testing.assert_array_equal(parsed['auxiliary_fit_1st'], self.isus_expected[:, 4])
        np.testing.assert_array_equal(parsed['auxiliary_fit_2nd'], self.isus_expected[:, 5])
        np.testing.assert_array_equal(parsed['auxiliary_fit_3rd'], self.isus_expected[:, 6])
        np.testing.assert_array_equal(parsed['rms_error'], self.isus_expected[:, 7])
        np.testing.assert_array_equal(parsed['temperature_internal'], self.isus_expected[:, 8])
        np.testing.assert_array_equal(parsed['temperature_spectrometer'], self.isus_expected[:, 9])
        np.testing.assert_array_equal(parsed['temperature_lamp'], self.isus_expected[:, 10])
        np.testing.assert_array_equal(parsed['lamp_on_time'], self.isus_expected[:, 11])
        np.testing.assert_array_equal(parsed['humidity'], self.isus_expected[:, 12])
        np.testing.assert_array_equal(parsed['voltage_lamp'], self.isus_expected[:, 13])
        np.testing.assert_array_equal(parsed['voltage_analog'], self.isus_expected[:, 14])
        np.testing.assert_array_equal(parsed['voltage_main'], self.isus_expected[:, 15])
        np.testing.assert_array_equal(parsed['average_reference'], self.isus_expected[:, 16])
        np.testing.assert_array_equal(parsed['variance_reference'], self.isus_expected[:, 17])
        np.testing.assert_array_equal(parsed['seawater_dark'], self.isus_expected[:, 18])
        np.testing.assert_array_equal(parsed['spectral_average'], self.isus_expected[:, 19])
        np.testing.assert_array_equal(np.array(parsed['channel_measurements']), self.isus_expected[:, 20:-1])

    def test_parse_nutnr_suna(self):
        """
        Test parsing of a SUNA outputting full ASCII frames as recorded by the DCL versus recovered instrument
        data loaded from a CSV file per basic processing from above
        """
        self.nutnr_suna.load_ascii()
        self.nutnr_suna.parse_data()
        parsed = self.nutnr_suna.data.toDict()

        np.testing.assert_array_equal(parsed['decimal_hours'], self.suna_expected[:, 2])
        np.testing.assert_array_equal(parsed['nitrate_concentration'], self.suna_expected[:, 3])
        np.testing.assert_array_equal(parsed['nitrogen_in_nitrate'], self.suna_expected[:, 4])
        np.testing.assert_array_equal(parsed['absorbance_254'], self.suna_expected[:, 5])
        np.testing.assert_array_equal(parsed['absorbance_350'], self.suna_expected[:, 6])
        np.testing.assert_array_equal(parsed['bromide_trace'], self.suna_expected[:, 7])
        np.testing.assert_array_equal(parsed['spectral_average'], self.suna_expected[:, 8])
        np.testing.assert_array_equal(parsed['dark_value'], self.suna_expected[:, 9])
        np.testing.assert_array_equal(parsed['integration_factor'], self.suna_expected[:, 10])
        np.testing.assert_array_equal(parsed['channel_measurements'], self.suna_expected[:, 11:267])
        np.testing.assert_array_equal(parsed['temperature_internal'], self.suna_expected[:, 267])
        np.testing.assert_array_equal(parsed['temperature_spectrometer'], self.suna_expected[:, 268])
        np.testing.assert_array_equal(parsed['temperature_lamp'], self.suna_expected[:, 269])
        np.testing.assert_array_equal(parsed['lamp_on_time'], self.suna_expected[:, 270])
        np.testing.assert_array_equal(parsed['humidity'], self.suna_expected[:, 271])
        np.testing.assert_array_equal(parsed['voltage_main'], self.suna_expected[:, 272])
        np.testing.assert_array_equal(parsed['voltage_lamp'], self.suna_expected[:, 273])
        np.testing.assert_array_equal(parsed['voltage_internal'], self.suna_expected[:, 274])
        np.testing.assert_array_equal(parsed['main_current'], self.suna_expected[:, 275])
        np.testing.assert_array_equal(parsed['fit_auxiliary_1'], self.suna_expected[:, 276])
        np.testing.assert_array_equal(parsed['fit_auxiliary_2'], self.suna_expected[:, 277])
        np.testing.assert_array_equal(parsed['fit_base_1'], self.suna_expected[:, 278])
        np.testing.assert_array_equal(parsed['fit_base_2'], self.suna_expected[:, 279])
        np.testing.assert_array_equal(parsed['fit_rmse'], self.suna_expected[:, 280])


if __name__ == '__main__':
    unittest.main()
