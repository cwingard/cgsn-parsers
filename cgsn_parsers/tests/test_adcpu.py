#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.tests.test_adcpu
@file cgsn_parsers/tests/test_adcpu.py
@author Christopher Wingard
@brief Unit tests for parsing the Nortek Aquadopp (ADCPU) DCL log data
"""
import numpy as np
import unittest

from os import path

from cgsn_parsers.parsers.parse_adcpu import Parser

TESTDATA = path.join(path.dirname(__file__), 'adcpu/20240720.aqua.log')


class TestParsingUnit(unittest.TestCase):
    """
    OOI moorings use the Nortek Aquadopp current profiler (ADCPU), logged in NMEA-like DCL sentences: $PNORI
    (configuration), $PNORS (sensor status), and $PNORC (per-cell current data).
    """
    def setUp(self):
        """
        Using the sample data file, initialize the Parser object and parse the data.
        """
        self.adcpu = Parser(TESTDATA)
        self.adcpu.load_ascii()
        self.adcpu.parse_data()

    def test_parse_adcpu_config(self):
        """
        Test parsing of the $PNORI configuration record.
        """
        config = self.adcpu.data.config
        self.assertEqual(config.dcl_datetime[0], '2024/07/20 00:05:28.689')
        self.assertEqual(config.instrument_type[0], 4)
        self.assertEqual(config.instrument_name[0], 'Aquadopp Profiler 1 MHz S1VP400277')
        self.assertEqual(config.number_beams[0], 3)
        self.assertEqual(config.number_cells[0], 45)
        self.assertEqual(config.blanking[0], 0.40)
        self.assertEqual(config.cell_size[0], 0.50)
        self.assertEqual(config.coord_system[0], 0)

    def test_parse_adcpu_sensor(self):
        """
        Test parsing of the $PNORS sensor status record.
        """
        sensor = self.adcpu.data.sensor
        self.assertEqual(sensor.dcl_datetime[0], '2024/07/20 00:05:28.735')
        self.assertEqual(sensor.sensor_datetime[0], 1721433029)
        self.assertEqual(self.adcpu.data.time[0], 1721433029)
        self.assertEqual(sensor.error_code[0], '00000000')
        self.assertEqual(sensor.status_code[0], '384D0002')
        self.assertEqual(sensor.battery_voltage[0], 10.9)
        self.assertEqual(sensor.sound_speed[0], 1534.5)
        self.assertEqual(sensor.heading[0], 224.3)
        self.assertEqual(sensor.pitch[0], -47.3)
        self.assertEqual(sensor.roll[0], 88.9)
        self.assertEqual(sensor.pressure[0], 0.686)
        self.assertEqual(sensor.temperature[0], 25.04)
        self.assertEqual(sensor.analog_in_1[0], 0)
        self.assertEqual(sensor.analog_in_2[0], 0)

    def test_parse_adcpu_current(self):
        """
        Test parsing of the first 9 $PNORC per-cell current records. This unit reports only 3 beams, so also
        confirms the optional beam 4 fields are filled with the documented sentinel values (NaN velocity, 0
        amplitude/correlation).
        """
        current = self.adcpu.data.current
        expected = np.array([
            # cell, vel_beam_1, vel_beam_2, vel_beam_3, speed, direction, amp_1, amp_2, amp_3, corr_1, corr_2, corr_3
            [1, -1.65, 1.81, -0.46, 2.45, 317.8, 82, 81, 80, 76, 79, 67],
            [2, -32.77, -32.77, -32.77, 46.34, 225.0, 107, 106, 105, 38, 39, 41],
            [3, 0.95, -0.91, -0.04, 1.31, 134.0, 112, 112, 110, 99, 100, 100],
            [4, 1.11, -1.06, -0.03, 1.53, 133.8, 117, 117, 115, 100, 100, 100],
            [5, 1.11, -1.05, -0.01, 1.53, 133.3, 118, 118, 116, 100, 100, 100],
            [6, 1.07, -1.02, -0.03, 1.48, 133.7, 118, 118, 116, 100, 100, 100],
            [7, 1.07, -1.02, -0.02, 1.48, 133.6, 118, 118, 116, 100, 100, 100],
            [8, 1.07, -1.03, -0.03, 1.49, 133.9, 118, 118, 116, 100, 100, 100],
            [9, 1.08, -1.03, -0.02, 1.49, 133.8, 118, 118, 116, 100, 100, 100],
        ])
        n = expected.shape[0]

        np.testing.assert_array_equal(current.cell_number[:n], expected[:, 0])
        np.testing.assert_array_equal(current.velocity_beam_1[:n], expected[:, 1])
        np.testing.assert_array_equal(current.velocity_beam_2[:n], expected[:, 2])
        np.testing.assert_array_equal(current.velocity_beam_3[:n], expected[:, 3])
        np.testing.assert_array_equal(current.speed[:n], expected[:, 4])
        np.testing.assert_array_equal(current.direction[:n], expected[:, 5])
        np.testing.assert_array_equal(current.amplitude_beam_1[:n], expected[:, 6])
        np.testing.assert_array_equal(current.amplitude_beam_2[:n], expected[:, 7])
        np.testing.assert_array_equal(current.amplitude_beam_3[:n], expected[:, 8])
        np.testing.assert_array_equal(current.correlation_beam_1[:n], expected[:, 9])
        np.testing.assert_array_equal(current.correlation_beam_2[:n], expected[:, 10])
        np.testing.assert_array_equal(current.correlation_beam_3[:n], expected[:, 11])

        self.assertTrue(np.all(np.isnan(current.velocity_beam_4[:n])))
        self.assertTrue(np.all(np.array(current.amplitude_beam_4[:n]) == 0))
        self.assertTrue(np.all(np.array(current.correlation_beam_4[:n]) == 0))
        self.assertTrue(np.all(np.array(current.amplitude_units[:n]) == 'C'))


if __name__ == '__main__':
    unittest.main()
