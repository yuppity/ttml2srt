#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import filecmp
import sys
import os
import subprocess

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '../')))

import ttml2srt

class Tester(unittest.TestCase):

    def file_tests(self, fname, cmd_exit_zero=True, cmp_result=True, args={}):

        e_args = [i for sl in \
                [[str(k), str(v)] for k, v in args.items()] for i in sl]

        run = subprocess.call(
            ['python2', 'ttml2srt.py'] + e_args + [fname, 'tests/testfile'])

        if cmd_exit_zero:
            self.assertEqual(run, 0)
        else:
            self.assertNotEqual(run, 0)

        filecmp._cache = {}  # FFS!
        fcmp = filecmp.cmp(fname.replace('.xml', '.srt'),
            'tests/testfile', False)

        if cmp_result:
            self.assertTrue(fcmp)
        else:
            self.assertFalse(fcmp)

    def test_time(self):

        ms_to_subrip_tests = (
            ('00:03:52,823', 232823),
            ('00:00:01,000', 1000),
            ('00:00:01,001', 1001),
            ('00:00:01,002', 1002),
            ('00:01:00,000', 60000),
            ('01:01:00,000', 3.6e6 + 60000),
            ('00:03:15,560', 195560),
            ('01:03:15,560', 3.6e6 + 195560),
            ('01:32:23,123', 5543123),
            ('01:01:01,999', 3.6e6 + 60000 + 1000 + 999),
            ('01:01:01,001', 3.6e6 + 60000 + 1000 + 1),
            ('01:01:01,000', 3.6e6 + 60000 + 1000 + 0),
            ('06:01:01,999', 3.6e6 * 6 + 60000 + 1000 + 999),
            ('99:59:59,999', 3.6e6 * 99 + 60000 * 59 + 59000 + 999),
            ('100:00:00,999', 3.6e6 * 99 + 3.6e6 + 0 + 999),
            ('00:00:00,001', 1),
        )

        for timestamp, ms in ms_to_subrip_tests:
            self.assertEqual(ttml2srt.ms_to_subrip(ms), timestamp)

        timestamp_to_ms_tests = (
            ('00:03:52.23', '.', 232959, 23.976),
            ('00:03:52.23', '.', 232920, 25),
            ('00:03:52,23', ',', 232920, 25),
            ('00:03:52:23', ':', 232920, 25),
            ('00:00:00.25', '.', 1000, 25),
            ('00:00:01.00', '.', 1000, 25),
        )

        for timestamp, sep, ms, fps in timestamp_to_ms_tests:
            self.assertEqual(ttml2srt.timestamp_to_ms(
                timestamp, fps=fps, delim=sep),
                ms)

        timestamp_to_subrip_tests = (
            ('00:00:10.23', '00:00:10,959', True, {}),
            ('00:02:10.23', '00:02:10,959', True, {}),
            ('03:02:10.23', '03:02:10,959', True, {}),
            ('10:02:10.23', '10:02:10,959', True, {}),
            ('01:01:00.00', '01:01:00,000', True, {'fps': 25}),
            ('01:03:15.14', '01:03:15,560', True, {'fps': 25}),
            ('10:03:15.14', '10:03:15,560', True, {'fps': 25}),
            ('00:00:10.23', '00:00:10,920', True, {'fps': 25}),
            ('00:00:10.23', '00:00:10,959', False, {'fps': 25}),
            ('00:00:10.23', '00:00:16,959', True, {'shift': 6000}),
        )

        for test in timestamp_to_subrip_tests:
            ttml_ts, expected_subrip_ts, equal, kwargs = test
            assertionFn = self.assertEqual if equal else self.assertNotEqual
            assertionFn(ttml2srt.get_sb_timestamp_be(
                ttml_ts, **kwargs), expected_subrip_ts)

        self.assertRaises(
            TypeError, ttml2srt.get_sb_timestamp_be, '131798332t')

    def test_foutput(self):
        self.file_tests('tests/cmore_sample.xml', True, True)
        self.file_tests('tests/netflix_sample.xml', True, True)
        self.file_tests('tests/hbo_nordic_sample.xml', True, True)
        self.file_tests('tests/hbo_nordic_sample.xml', True, False, {'-f': 5})
        self.file_tests('tests/hbo_nordic_sample.xml', True, False, {'-s': 5000})
        self.file_tests('tests/netflix_t_overlap01.xml', True, True)

if __name__ == '__main__':
    unittest.main()
