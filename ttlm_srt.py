#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import print_function
from xml.dom import minidom

def calc_scale(sdur, tdur): return (tdur * 1.0) / sdur

def scaler(scaling, time): return int(scaling * time)

def frames_to_ms(frames, fps = 23.976):
    frames = int(frames)
    return int(frames * (1000 / fps))

def ticks_to_ms(tickrate, ticks):
    ticks = int(ticks.rstrip('t'))
    return ((1.0 / tickrate) * ticks) * 1000

def ms_to_subrip(ms):
    return '{:02d}:{:02d}:{:02d},{:03d}'.format(
            int(ms / (3600 * 1000)),   # hh
            int(ms / 60000),           # mm
            int((ms % 60000) / 1000),  # ss
            int((ms % 60000) % 1000))  # ms

def timestamp_to_ms(time, delim = '.'):
    hhmmss, ms = time.rsplit(delim, 1)
    hhmmss = hhmmss.split(':')
    hh, mm, ss = [int(hhmmss[0]) * 3600 * 1000,
                  int(hhmmss[1]) * 60 * 1000,
                  int(hhmmss[2]) * 1000]
    return hh + mm + ss + int(ms)

def get_sb_timestamp_be(time, shift = 0, fps = 23.976, tick_rate = None):
    """Return SubRip timestamp after conversion from source timestamp.

    Assumes source timestamp to be in either the form of
        [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}[,.:]{0-9}{1,3}
    or
        [0-9]*t?$

    Examples of valid timestamps: '00:43:30:07', '00:43:30.07',
    '00:43:30,07', '130964166t'.

    Assumes that all field separated four value timestamps map
    to 'hour:minute:second:frame'.
    """

    delim = ''.join([i for i in time if not i.isdigit()])[-1]
    if delim.lower() == 't':
        ms = ticks_to_ms(tick_rate, time)
    else:
        hhmmss, frames = time.rsplit(delim, 1)
        ms = timestamp_to_ms(delim.join([hhmmss, str(frames_to_ms(frames, fps))]), delim = delim)

    return ms_to_subrip(ms + shift)

if __name__ == '__main__':
    import argparse
    import sys

    argparser = argparse.ArgumentParser(
            description = 'Convert subtitles from TTML Document to SubRip (SRT).')
    argparser.add_argument('ttml-file',
            help = 'TTML subtitle file',
            action = 'store')
    argparser.add_argument('-s', '--shift',
            dest = 'shift', help = 'shift',
            metavar = 'ms', nargs = '?',
            const = 0, default = 0, type = int,
            action = 'store')
    argparser.add_argument('-f', '--fps',
            dest = 'sfps', metavar = 'fps',
            help = 'frames per second (default: 23.976)',
            nargs = '?', const = 23.976,
            default = 23.976, type = float,
            action = 'store')
    argparser.add_argument('--t-dur',
            dest = 'td', metavar = 'sec',
            help = 'target duration',
            nargs = '?', type = int, default = 0, action = 'store')
    argparser.add_argument('--s-dur',
            dest = 'sd', metavar = 'sec',
            help = 'source duration',
            nargs = '?', type = int, default = 0, action = 'store')
    args = argparser.parse_args()

    time_multiplier = False
    if args.subfile == None: sys.exit(2)
    if args.td > 0 and args.sd > 0:
        time_multiplier = calc_scale(args.sd, args.td)

    def extract_dialogue(nodes):
        dialogue = ''
        for node in nodes:
            if node.localName == 'br': dialogue = dialogue + '\n'
            elif node.nodeValue: dialogue = dialogue + node.nodeValue
            if node.hasChildNodes(): dialogue = dialogue + extract_dialogue(node.childNodes)
        return dialogue

    subd = minidom.parse(args.subfile)
    if subd.encoding.lower() not in ['utf8', 'utf-8']:
        # Don't attempt to convert subtitles that are not in UTF-8.
        # Why? Out of spite.
        print('Source is not declared as utf-8')
        sys.exit(1)

    # Get the root tt element (assume the file contains
    # a single subtitle document)
    tt_element = subd.getElementsByTagName('tt')[0]

    # Detect source FPS and tick rate
    try: fps = int(tt_element.attributes['ttp:frameRate'].value)
    except KeyError: fps = args.sfps
    try: tick_rate = int(tt_element.attributes['ttp:tickRate'].value)
    except KeyError: tick_rate = None

    lines = [i for i in subd.getElementsByTagName('p') if 'begin' in i.attributes.keys()]

    lcount = 0
    for line in lines:
        lcount = lcount + 1
        print('{}\n{} --> {}\n{}\n'.format(lcount,
            get_sb_timestamp_be(line.attributes['begin'].value, args.shift, fps, tick_rate),
            get_sb_timestamp_be(line.attributes['end'].value, args.shift, fps, tick_rate),
            extract_dialogue(line.childNodes).encode('utf8')))

