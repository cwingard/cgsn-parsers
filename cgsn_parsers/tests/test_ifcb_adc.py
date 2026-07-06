#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@package cgsn_parsers.tests.test_ifcb_adc
@file cgsn_parsers/tests/test_ifcb_adc.py
@author Christopher Wingard
@brief Unit tests for parsing the McLean IFCB .adc feature file, using column names sourced from the
    companion .hdr file.
"""
import unittest

from os import path

from cgsn_parsers.parsers.parse_ifcb_adc import HdrParser, AdcParser

RAWDATA_HDR = path.join(path.dirname(__file__), 'ifcb/D20230222T174812_IFCB195.hdr')
RAWDATA_ADC = path.join(path.dirname(__file__), 'ifcb/D20230222T174812_IFCB195.adc')


class TestParsingUnit(unittest.TestCase):
    """
    OOI Pioneer MAB moorings use the McLane IFCB sensor. The .adc file is a CSV-formatted per-trigger feature
    file whose column order is defined by the ADCFileFormat line in the companion .hdr file; this test mirrors
    that two-step process. Note the parser stores every value as the raw string token from the file (no type
    conversion), which is preserved here rather than "improved" ahead of a dedicated consistency pass.
    """
    def setUp(self):
        """
        Using the sample .hdr and .adc files, derive the column order from the header and then parse the
        .adc feature file.
        """
        hdr = HdrParser(RAWDATA_HDR)
        hdr.load_ascii()
        hdr.parse_data()
        self.cols = hdr.data['ADCFileFormat'][0].split(', ')

        self.adc = AdcParser(RAWDATA_ADC, self.cols)
        self.adc.load_ascii()
        self.adc.parse_data()

    def test_parse_ifcb_adc(self):
        """
        Test parsing of the first 3 rows of the .adc feature file against values transcribed directly from
        the raw CSV file.
        """
        expected_rows = [
            ['1', '0.0501559', '0.011896491', '0.027126074', '0.004928112', '0.0030642748', '0.24540663',
             '0.55245876', '0.011234283', '0.010864735', '60.869564', '0.0501559', '0.09265430000000001',
             '0', '0', '0', '0', '0', '0', '0', '0', '0', '0.07159288194444445', '0'],
            ['2', '5.9189884', '0.010858774', '0.027797222', '0.0048160553', '0.0030511618', '0.22957087',
             '0.56899786', '0.011239052', '0.0108242035', '58.695652', '5.9189884', '5.9677474',
             '804', '422', '80', '60', '0', '0', '0', '0', '0', '5.946644965277778', '0.07771267361111112'],
            ['3', '6.0378881', '0.012244582', '0.028951168', '0.0049090385', '0.0030857325', '0.27556896',
             '0.5973983', '0.011258125', '0.010857582', '60.869564', '6.0378881', '6.0882188',
             '804', '366', '72', '52', '4800', '0', '0', '0', '0', '6.0657769097222225', '0.16614149305555556'],
        ]

        self.assertEqual(len(self.adc.data[self.cols[0]]), 8845)
        for i, row in enumerate(expected_rows):
            for col, value in zip(self.cols, row):
                self.assertEqual(self.adc.data[col][i], value)


if __name__ == '__main__':
    unittest.main()
