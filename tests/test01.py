#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import filecmp
import sys, os
import subprocess

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../')))
import ttml2srt

class TestyTester(unittest.TestCase):
    def file_tests(self, fname, cmd_exit_zero = True, cmp_result = True, args = {}):
        e_args = [i for sl in [[str(k), str(v)] for k, v in args.iteritems()] for i in sl]
        run = subprocess.call(['python2', 'ttml2srt.py'] + e_args + [fname, 'tests/testfile'])
        if cmd_exit_zero: self.assertEqual(run, 0)
        else: self.assertNotEqual(run, 0)

        filecmp._cache = {} # FFS!
        fcmp = filecmp.cmp(fname.replace('.xml', '.srt'), 'tests/testfile', False)

        if cmp_result: self.assertTrue(fcmp)
        else: self.assertFalse(fcmp)

    def test_time(self):
        self.assertEqual(ttml2srt.ms_to_subrip(232823), '00:03:52,823')
        self.assertEqual(ttml2srt.ms_to_subrip(1000), '00:00:01,000')
        self.assertEqual(ttml2srt.ms_to_subrip(60000), '00:01:00,000')

        self.assertEqual(ttml2srt.timestamp_to_ms('00:03:52.23', 23.976, '.'), 232959)
        self.assertEqual(ttml2srt.timestamp_to_ms('00:03:52.23', 25, '.'), 232920)
        self.assertEqual(ttml2srt.timestamp_to_ms('00:03:52,23', 25, ','), 232920)
        self.assertEqual(ttml2srt.timestamp_to_ms('00:03:52:23', 25, ':'), 232920)
        self.assertEqual(ttml2srt.timestamp_to_ms('00:00:00.25', 25, '.'), 1000)
        self.assertEqual(ttml2srt.timestamp_to_ms('00:00:01.00', 25, '.'), 1000)

        self.assertEqual(ttml2srt.get_sb_timestamp_be('00:00:10.23'), '00:00:10,959')
        self.assertNotEqual(ttml2srt.get_sb_timestamp_be('00:00:10.23', fps = 25), '00:00:10,959')
        self.assertEqual(ttml2srt.get_sb_timestamp_be('00:00:10.23', shift = 6000), '00:00:16,959')
        self.assertRaises(TypeError, ttml2srt.get_sb_timestamp_be, '131798332t')

    def test_foutput(self):
        self.file_tests('tests/cmore_sample.xml', True, True)
        self.file_tests('tests/netflix_sample.xml', True, True)
        self.file_tests('tests/hbo_nordic_sample.xml', True, True)
        self.file_tests('tests/hbo_nordic_sample.xml', True, False, {'-f': 5})
        self.file_tests('tests/hbo_nordic_sample.xml', True, False, {'-s': 5000})

if __name__ == '__main__':
    unittest.main()
