# -*- coding: utf-8 -*-

import unittest
import filecmp
import sys
import os
import subprocess
import re

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '../')))

from ttml2srt import Ttml2Srt

SAMPLE_DIR = 'tests/ttml-documents'

def get_ttml(**kwargs):
    return Ttml2Srt(os.path.join(SAMPLE_DIR, 'netflix-077.xml'), **kwargs)

def set_attrs(ttml, fps=None, clock_mode=None, tick_rate=None, time_base = None):
    if fps is not None:
        ttml.frame_rate = fps
    if clock_mode is not None:
        ttml.clock_mode = clock_mode
    if tick_rate is not None:
        ttml.tick_rate = tick_rate
    if time_base is not None:
        ttml.time_base = time_base

class Tester(unittest.TestCase):

    def test_time_expr_type_detection(self):

        ttml = get_ttml()

        timestamp_type_tests = (
            ('00:00:10:23', ttml.frame_timestamp_to_ms),
            ('00:00:10:23.2', ttml.frame_timestamp_to_ms),
            ('00:00:10.23', ttml.fraction_timestamp_to_ms),
            ('520520000t', ttml.offset_ticks_to_ms),
            ('2.23s', ttml.offset_seconds_to_ms),
            ('2.2986020106233s', ttml.offset_seconds_to_ms),
            ('983698264986234ms', ttml.offset_ms_to_ms),
            ('923f', ttml.offset_frames_to_ms),
            ('923f', ttml.offset_frames_to_ms),
        )

        for t in timestamp_type_tests:
            self.assertEqual(
                ttml.determine_ms_convfn(t[0]), t[1])

        self.assertRaises(
            NotImplementedError, ttml.determine_ms_convfn, '4322323')

    def test_clock_time_frame_expressions(self):

        ttml = get_ttml()

        clocktime_frame_timestamp_tests = (
            ('00:00:00:01', 25, 40),
            ('00:00:01:01', 25, 1000 + 40),
            ('00:01:01:01', 25, 60000 + 1000 + 40),
            ('01:01:01:01', 25, 3.6e6 + 60000 + 1000 + 40),
            ('01:01:01:01.231', 25, 3.6e6 + 60000 + 1000 + 40),
            ('00:00:01:01.0003', 25, 1000 + 40),
        )

        for t in clocktime_frame_timestamp_tests:
            set_attrs(ttml, *t[1:-1])
            self.assertEqual(ttml.frame_timestamp_to_ms(t[0]), t[-1])
            self.assertEqual(ttml.timeexpr_to_ms(t[0]), t[-1])

    def test_clock_time_fraction_expressions(self):

        ttml = get_ttml()

        clocktime_frame_timestamp_tests = (
            ('00:00:00.001', 25, 1),
            ('00:00:00.001', 205, 1),
            ('01:01:01.231', 25, 3.6e6 + 60000 + 1000 + 231),
        )

        for t in clocktime_frame_timestamp_tests:
            set_attrs(ttml, *t[1:-1])
            self.assertEqual(ttml.fraction_timestamp_to_ms(t[0]), t[-1])
            self.assertEqual(ttml.timeexpr_to_ms(t[0]), t[-1])

    def test_offset_time_expressions(self):

        ttml = get_ttml()

        seconds_to_ms_tests = (
            ('1.0s', 1000),
            ('1.1s', 1100),
        )

        for t in seconds_to_ms_tests:
            self.assertEqual(ttml.offset_seconds_to_ms(t[0]), t[1])

        minutes_to_ms_tests = (
            ('1.0m', 60 * 1000),
            ('1.2m', 60 * 1000 + 12 * 1000),
        )

        for t in minutes_to_ms_tests:
            self.assertEqual(ttml.offset_minutes_to_ms(t[0]), t[1])

        hours_to_ms_tests = (
            ('1.0h', 3.6e6),
            # ('1.2h', 60 * 1000 + 12 * 1000),
        )

        for t in hours_to_ms_tests:
            self.assertEqual(ttml.offset_hours_to_ms(t[0]), t[1])

    def test_ms_to_subrip(self):

        ttml = get_ttml()

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
            self.assertEqual(ttml.ms_to_subrip(ms), timestamp)

    def test_timeexpr_to_ms(self):

        timestamp_to_subrip_tests = (
            # time exrp, subrip timecode, assertion, attrs (set_attrs()), kwargs
            ('00:00:10:23', '00:00:10,959', True, {}, {}),
            ('00:02:10:23', '00:02:10,959', True, {}, {}),
            ('03:02:10:23', '03:02:10,959', True, {}, {}),
            ('10:02:10:23', '10:02:10,959', True, {}, {}),
            ('01:01:00:00', '01:01:00,000', True, [25], {}),
            ('01:03:15:14', '01:03:15,560', True, [25], {}),
            ('10:03:15:14', '10:03:15,560', True, [25], {}),
            ('00:00:10:23', '00:00:10,920', True, [25], {}),
            ('00:00:10:23.232', '00:00:10,920', True, [25], {}),
            ('00:00:10:23', '00:00:10,959', False, [25], {}),
            ('00:00:10:23', '00:00:16,959', True, [], {'shift': 6000}),
            ('02:01:59.999', '02:01:59,999', True, [60], {}),
        )

        for test in timestamp_to_subrip_tests:
            time_expr, subrip, equal, attrs, kwargs = test
            ttml = get_ttml(**kwargs)
            set_attrs(ttml, *attrs)
            convfn = ttml.determine_ms_convfn(time_expr)
            (self.assertEqual if equal else self.assertNotEqual)(
                ttml.timeexpr_to_subrip(time_expr)[1],
                subrip)

    def test_time_positions(self):

        positions = {

            # TTML document path
            'brooklyn.nine-nine.s02e19.netflix.en.xml': (

                # line to match, expected time position, margin of error in ms
                ('Well, that\'s great news, sir.', 1218.043 * 1000, 500),
            ),

            'rotten.netflix.en.xml': (
                ('a food to be eaten every day.', 33.434 * 1000, 500),
                ('At the bottom is the exit tube.', 2303.821 * 1000, 500),
                ('but they guzzle a shringking water supply.', 3206.242 * 1000, 250),

            ),

            'darkest.hour.netflix.en.xml': (
                ('under the leadership of Mr. Chamberlain', 231.443 * 1000, 500),
                ('Uh, Neville, would you...', 4009.489 * 1000, 500),
                ('There shall be no negotiated peace.', 6705.056 * 1000, 500),
            ),

            'succession.s01e01.hbo-nordic.en.xml': (
                ('Where am I?', 38 * 1000, 1000),
                ('Has he fainted?', (54 * 60 + 10) * 1000, 1000),
            ),

        }

        for ttml_file in positions.keys():
            ttml = Ttml2Srt(os.path.join(SAMPLE_DIR, ttml_file))
            subs = sorted(
                [ttml.process_parag(p) for p in ttml.lines], key=lambda x: x[0])
            position_pairings = positions[ttml_file]
            for line_match, pos, margin in position_pairings:
                for bms, ems, _b, _e, line in subs:
                    if line.strip() == line_match:
                        try:
                            self.assertTrue(
                                bms <= pos + margin and bms >= pos - margin)
                        except AssertionError:
                            raise AssertionError(
                                'calculated pos: {}, wanted: {}, margin: {}'.format(
                                    bms, pos, margin))

    def test_files(self):
        with open(os.devnull, 'w') as f:
            for ttml_doc in os.listdir(SAMPLE_DIR):
                ttml = Ttml2Srt(os.path.join(SAMPLE_DIR, ttml_doc))
                for p in ttml.paragraphs(generator=True):
                    f.write(p)

if __name__ == '__main__':
    unittest.main()
