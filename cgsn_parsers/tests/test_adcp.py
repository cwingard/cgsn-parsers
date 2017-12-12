#!/usr/bin/env python
# -*-coding: utf-8 -*-
"""
@package cgsn_parsers.tests.test_adcp
@file cgsn_parsers/tests/test_adcp.py
@author Christopher Wingard
@brief Unit tests for parsing the 2 different types of ADCP data
"""
import numpy as np
import unittest

from nose.plugins.attrib import attr
from os import path

from cgsn_parsers.parsers.parse_adcp import Parser

TESTDATA_PD0 = path.join(path.dirname(__file__), 'adcp/20160617.adcpt.log')
TESTDATA_PD8 = path.join(path.dirname(__file__), 'adcp/20150515.adcp.log')


@attr('parse')
class TestParsingUnit(unittest.TestCase):
    """
    OOI Endurance and Pioneer moorings use the Teledyne RDI Workhorse ADCPs on the NSIF and MFN instrument frames, 
    configured to output the data in either PD0 format (Endurance) or PD8 format (Pioneer). All units are set to output
    the velocity data in Earth Coordinates.

    This test class will parse and compare the outputs from the two types of ADCPs to confirm the parser functions
    as expected.
    """
    def setUp(self):
        """
        Using sample data files, initialize the Parser objects for each of the 2 ADCP types and setup the expected
        output arrays.
        """
        # initialize Parser objects for the CTDBP types defined above.
        self.adcp_pd0 = Parser(TESTDATA_PD0, 0)
        self.adcp_pd8 = Parser(TESTDATA_PD8, 8)

        # Set the expected output arrays for the PD0 formatted data. Expected data created using WinADCP on recovered
        # data from the Spring 2016 deployment of CE02SHSM, focusing specifically on data from 2016-06-17. Source data
        # can be found:
        #
        #   https://rawdata.oceanobservatories.org/files/CE02SHSM/R00003/instrmts/dcl26/ADCPT_sn18222/
        #
        # Expected data limited to ensemble number, real time clock, heading, pitch, roll and the first 5 bins of the
        # eastward and northward velocities. Limited to first 12 hours of the day. These elements are spread throughout
        # the data file. Thus, if the parsing had failed, the whole house of cards should come apart and none of these
        # elements will match
        self.pd0 = np.array([
            [2892, 16, 6, 17, 0, 0, -2.65, -0.65, 265.7, -59, -61, -49, -17, 17, -253, -251, -225, -220, -178],
            [2893, 16, 6, 17, 0, 15, -1.93, -2.84, 276.07, -110, -80, -79, -17, 36, -238, -226, -229, -172, -106],
            [2894, 16, 6, 17, 0, 30, -4.78, -1.38, 241.77, -74, -60, 34, 69, 41, -227, -188, -170, -126, -131],
            [2895, 16, 6, 17, 0, 45, -2.12, 2.53, 208.33, -66, -27, 11, 53, 68, -180, -183, -177, -177, -184],
            [2896, 16, 6, 17, 1, 0, -3.78, 0.9, 218.65, -25, 0, 7, 1, -23, -178, -195, -202, -217, -210],
            [2897, 16, 6, 17, 1, 15, -2.96, -0.2, 286.4, -62, 20, 49, 41, -2, -141, -146, -187, -240, -229],
            [2898, 16, 6, 17, 1, 30, -0.18, 0.11, 340.49, -42, -40, 6, 52, 49, -181, -183, -171, -145, -176],
            [2899, 16, 6, 17, 1, 45, -2.26, 0.38, 271.25, 2, 55, 53, 46, 13, -137, -182, -194, -209, -214],
            [2900, 16, 6, 17, 2, 0, -0.03, -0.7, 1.28, -30, 17, 101, 84, 58, -205, -204, -224, -260, -290],
            [2901, 16, 6, 17, 2, 15, -0.39, 1.99, 86.83, -63, -71, -34, 4, 40, -138, -141, -153, -145, -139],
            [2902, 16, 6, 17, 2, 30, -0.69, 0.84, 69.92, -32, 17, 51, 115, 140, -185, -178, -187, -219, -229],
            [2903, 16, 6, 17, 2, 45, -1, 2.59, 85.3, -2, -16, 16, 66, 126, -167, -182, -173, -190, -191],
            [2904, 16, 6, 17, 3, 0, -0.65, 3.12, 65.07, -15, -26, -21, 27, 86, -207, -257, -243, -258, -257],
            [2905, 16, 6, 17, 3, 15, -2.12, 3.05, 96.31, 4, 21, 79, 144, 174, -185, -177, -212, -233, -233],
            [2906, 16, 6, 17, 3, 30, 1.42, 2.8, 52.88, 72, 128, 176, 191, 163, -178, -216, -234, -241, -248],
            [2907, 16, 6, 17, 3, 45, -0.99, 4.16, 87.13, 51, 92, 130, 146, 122, -121, -151, -200, -218, -235],
            [2908, 16, 6, 17, 4, 0, -2.01, 2.4, 109.67, -15, 19, 84, 73, 74, -212, -244, -272, -298, -325],
            [2909, 16, 6, 17, 4, 15, 0.8, 4.32, 70.82, -39, -1, 45, 86, 88, -173, -200, -202, -222, -271],
            [2910, 16, 6, 17, 4, 30, -0.34, 5.83, 89.87, -41, -19, 28, 58, 68, -131, -174, -203, -246, -294],
            [2911, 16, 6, 17, 4, 45, -1.87, 6.71, 97.76, -29, -72, -48, -34, -12, -148, -136, -164, -210, -253],
            [2912, 16, 6, 17, 5, 0, -0.98, 8.42, 95.52, -73, -71, -37, -35, -30, -181, -169, -206, -273, -298],
            [2913, 16, 6, 17, 5, 15, -0.04, 9.05, 91.21, -9, -39, -24, -11, 29, -175, -166, -164, -208, -244],
            [2914, 16, 6, 17, 5, 30, -0.82, 10.98, 93.23, -78, -75, -56, -49, -33, -238, -217, -240, -276, -311],
            [2915, 16, 6, 17, 5, 45, -1.36, 11.93, 100.46, 6, -15, -19, -3, -3, -178, -180, -189, -189, -262],
            [2916, 16, 6, 17, 6, 0, -1.23, 12.92, 98.11, 50, 23, 1, -27, -52, -214, -224, -206, -210, -219],
            [2917, 16, 6, 17, 6, 15, -1.35, 13.9, 98.2, 51, 30, 19, -7, -54, -201, -202, -229, -217, -194],
            [2918, 16, 6, 17, 6, 30, -1.46, 14.8, 96.55, 51, 76, 90, 44, -26, -163, -160, -210, -207, -183],
            [2919, 16, 6, 17, 6, 45, -1.27, 15.04, 98.82, 32, 32, 8, -16, -56, -137, -133, -177, -170, -164],
            [2920, 16, 6, 17, 7, 0, -0.78, 15.18, 104.8, 57, 20, -51, -54, -62, -166, -187, -172, -183, -208],
            [2921, 16, 6, 17, 7, 15, -0.72, 16.09, 105.82, 25, 20, -44, -76, -59, -186, -228, -207, -221, -240],
            [2922, 16, 6, 17, 7, 30, -1.87, 15.11, 107.66, 86, 87, 105, 47, -1, -195, -224, -248, -258, -236],
            [2923, 16, 6, 17, 7, 45, -0.93, 15.43, 99.1, 81, 98, 52, 2, -34, -208, -233, -243, -245, -217],
            [2924, 16, 6, 17, 8, 0, -1.54, 15.83, 102.99, 71, 74, 30, -35, -85, -266, -274, -271, -254, -221],
            [2925, 16, 6, 17, 8, 15, -3.09, 15.24, 115.11, 55, 46, 25, -40, -97, -250, -265, -264, -263, -230],
            [2926, 16, 6, 17, 8, 30, -2.72, 16.47, 112.56, 53, 68, 16, -35, -72, -264, -283, -287, -253, -219],
            [2927, 16, 6, 17, 8, 45, -2.56, 15.77, 108.28, 34, 53, 55, 49, -1, -308, -304, -338, -325, -282],
            [2928, 16, 6, 17, 9, 0, -0.2, 16.96, 98.23, 2, 60, 48, 6, -30, -339, -342, -336, -302, -303],
            [2929, 16, 6, 17, 9, 15, -1.54, 16.23, 93.49, 52, 83, 92, 77, 26, -344, -354, -352, -331, -306],
            [2930, 16, 6, 17, 9, 30, -1.06, 16.47, 95.07, -6, 44, 75, 31, 11, -294, -320, -300, -297, -286],
            [2931, 16, 6, 17, 9, 45, -0.92, 14.93, 92.3, 5, -7, -22, 2, -19, -248, -263, -259, -291, -302],
            [2932, 16, 6, 17, 10, 0, -1.44, 16.48, 92.37, -57, -59, -66, -84, -124, -285, -294, -301, -324, -274],
            [2933, 16, 6, 17, 10, 15, -3.08, 15.89, 101.22, -42, -63, -90, -98, -54, -309, -331, -361, -345, -286],
            [2934, 16, 6, 17, 10, 30, -3.26, 17.03, 105.22, -45, -63, -115, -109, -59, -290, -321, -318, -256, -236],
            [2935, 16, 6, 17, 10, 45, -3.42, 12.16, 107.71, -25, -20, -36, -87, -97, -301, -301, -327, -323, -311],
            [2936, 16, 6, 17, 11, 0, -5.82, 11.06, 120.7, -53, -67, -98, -102, -52, -244, -268, -283, -228, -219],
            [2937, 16, 6, 17, 11, 15, -4.93, 11.67, 112.19, -26, -47, -92, -59, -33, -287, -282, -287, -265, -260],
            [2938, 16, 6, 17, 11, 30, -5.29, 11.37, 118.75, -11, -28, -59, -34, -24, -338, -332, -324, -285, -273],
            [2939, 16, 6, 17, 11, 45, -4.28, 11.81, 112.61, -95, -75, -66, -60, -60, -285, -258, -257, -271, -288]
        ])

        # Set the expected output arrays for the PD8 formatted data. Expected data created using WinADCP on recovered
        # data from the Spring 2015 deployment of CP01CNSM, focusing specifically on data from 2015-05-15. Source data
        # can be found:
        #
        #   https://rawdata.oceanobservatories.org/files/CP01CNSM/R00003/cg_data/dcl35/ADCP_sn18593/
        #
        # Expected data limited to ensemble number, heading, pitch, roll and the first 5 bins of the eastward and
        # northward velocities. These elements are spread throughout the data file. Thus, if the parsing had failed,
        # the whole house of cards should come apart and none of these elements will match
        self.pd8 = np.array([
            [784, -1.6, -0.6, 166.5, -12, -9, -29, -16, -5, 48, 27, 17, 7, 8],
            [792, -1.6, -0.6, 166.6, -6, -4, -10, -4, 20, 69, 64, 77, 75, 77],
            [796, -1.6, -0.6, 166.5, -29, -19, -5, 3, 4, 57, 48, 56, 72, 24],
            [800, -1.6, -0.6, 166.5, 7, -29, 1, 14, 10, 81, 75, 85, 55, 70],
            [804, -1.6, -0.6, 166.5, 71, 47, 71, 75, 81, 83, 60, 63, 62, 31],
            [808, -1.6, -0.6, 166.5, 86, 75, 43, 53, 56, 96, 89, 91, 102, 68],
            [812, -1.6, -0.6, 166.4, 91, 65, 79, 79, 89, 30, 61, 58, 40, 38],
            [816, -1.5, -0.6, 166.5, -21, -26, -45, -23, -35, -48, -55, -51, -38, -71],
            [820, -1.6, -0.6, 166.5, -13, 0, -13, 12, 16, -20, -13, 10, 24, 3],
            [824, -1.6, -0.6, 166.6, 24, 35, 57, 48, 46, 3, 5, 21, 41, 47],
            [828, -1.6, -0.6, 166.5, 7, 3, -14, -34, -32, -58, -50, -40, -17, -21],
            [832, -1.6, -0.6, 166.6, -18, -19, -16, -15, -12, -14, 5, -8, 8, 14],
            [836, -1.6, -0.6, 166.6, 12, 10, 35, 44, 49, 14, 22, 39, 26, 41],
            [840, -1.6, -0.6, 166.6, -19, -37, -11, -2, 8, 4, 7, 8, 33, 34],
            [844, -1.6, -0.6, 166.6, -12, -13, 1, 35, 39, 67, 49, 61, 46, 40],
            [848, -1.6, -0.6, 166.5, 13, 24, 15, 11, 3, 69, 38, 59, 41, 35],
            [852, -1.6, -0.6, 166.5, 12, 13, 9, 8, 9, 33, 25, 2, 25, 40],
            [856, -1.6, -0.6, 166.5, 6, 6, 34, 22, 33, 12, 4, 44, 45, 32]
        ])

    def test_adcp_pd0(self):
        """
        Test parsing of a PD0 formatted data file
        """
        self.adcp_pd0.load_binary()
        self.adcp_pd0.parse_data()
        parsed = self.adcp_pd0.data.toDict()

        # compare ensemble number and real time clock arrays
        ensemble = np.atleast_1d(parsed['variable']['ensemble_number'])[:48]
        clock = np.atleast_2d(parsed['variable']['real_time_clock1'])[:48, :5]

        np.testing.assert_array_equal(ensemble, self.pd0[:, 0])
        np.testing.assert_array_equal(clock, self.pd0[:, 1:6])

        # compare heading, pitch and roll
        heading = np.atleast_1d(parsed['variable']['heading'][:48]) / 100.  # data is reported in decidegrees
        pitch = np.atleast_1d(parsed['variable']['pitch'][:48]) / 100.  # data is reported in decidegrees
        roll = np.atleast_1d(parsed['variable']['roll'][:48]) / 100.  # data is reported in decidegrees

        np.testing.assert_array_equal(heading, self.pd0[:, 8])
        np.testing.assert_array_equal(pitch, self.pd0[:, 6])
        np.testing.assert_array_equal(roll, self.pd0[:, 7])

        # compare eastward and northward velocities
        eastward = np.atleast_2d(parsed['velocity']['eastward'])[:48, :5]
        northward = np.atleast_2d(parsed['velocity']['northward'])[:48, :5]

        np.testing.assert_array_equal(eastward, self.pd0[:, 9:14])
        np.testing.assert_array_equal(northward, self.pd0[:, 14:])

    def test_adcp_pd8(self):
        """
        Test parsing of a PD8 formatted data file.
        """
        self.adcp_pd8.load_binary()
        self.adcp_pd8.parse_data()
        parsed = self.adcp_pd8.data.toDict()

        # compare ensemble number
        ensemble = np.atleast_1d(parsed['variable']['ensemble_number'])
        np.testing.assert_array_equal(ensemble, self.pd8[:, 0])

        # compare heading, pitch and roll
        heading = np.atleast_1d(parsed['variable']['heading'])
        pitch = np.atleast_1d(parsed['variable']['pitch'])
        roll = np.atleast_1d(parsed['variable']['roll'])

        np.testing.assert_array_equal(heading, self.pd8[:, 3])
        np.testing.assert_array_equal(pitch, self.pd8[:, 1])
        np.testing.assert_array_equal(roll, self.pd8[:, 2])

        # compare eastward and northward velocities
        eastward = np.atleast_2d(parsed['velocity']['eastward'])[:, :5]
        northward = np.atleast_2d(parsed['velocity']['northward'])[:, :5]

        np.testing.assert_array_equal(eastward, self.pd8[:, 4:9])
        np.testing.assert_array_equal(northward, self.pd8[:, 9:])


if __name__ == '__main__':
    unittest.main()
