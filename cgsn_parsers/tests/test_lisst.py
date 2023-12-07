"""
@package cgsn_parsers.tests.test_parse_lisst
@file cgsn_parsers/tests/test_parse_lisst.py
@author Samuel Dahlberg
@brief Unit tests for parsing the LISST instrument data
"""
import numpy as np
import unittest

from nose.plugins.attrib import attr
from os import path

from cgsn_parsers.parsers.parse_lisst import Parser

# data sources for testing the parser
RAWDATA = path.join(path.dirname(__file__), 'lisst/lisst.log')
EXPECTED = path.join(path.dirname(__file__), 'lisst/lisst_expected.txt')


@attr('parse')
class TestParsingUnit(unittest.TestCase):
    """
    This unit test will parse sample log code derived from the LISST Logger, and check key
    data outputs as well as select engineer data to validate the output variables.
    """
    def setUp(self):
        """
        Using the sample data, initialize the Parser object with parsed LISST
        data and set the expected output arrays.
        """
        # initialize Parser objects.
        self.lisst = Parser(RAWDATA)
        self.lisst.load_ascii()
        self.lisst.parse_data()

        # set the expected output array.
        self.expected = np.genfromtxt(EXPECTED, delimiter=",")

    def test_parse_optaa(self):
        """
        Test parsing of the LISST data file. Choosing random data columns to verify.
        """
        lisst_concentration = np.array(self.lisst.data.lisst_volume_concentration)
        mean_diameter = np.array(self.lisst.data.mean_diameter)
        year = np.array(self.lisst.data.second)
        pressure = np.array(self.lisst.data.pressure)

        np.testing.assert_array_equal(lisst_concentration[0, :], self.expected[1:37])
        np.testing.assert_array_equal(year, self.expected[47])
        np.testing.assert_array_equal(mean_diameter, self.expected[48])
        np.testing.assert_array_equal(pressure, self.expected[51])


if __name__ == '__main__':
    unittest.main()
