# ttml2srt
Convert TTML subtitles used by Netflix, HBO, CMore and others to SRT format.

`ttml2srt` is *not* a full-featured TTML-to-SRT converter and only works on a small subset of TTML documents. Namely, documents that follow the formats seen on the aforementioned streaming services.  Parts of the spec that you might expect support for that nevertheless aren't supported include overlapping time intervals, text styling (italics, etc.), and regions.

Note: I'll happily relinquish the repo name if you want to host a more full-featured, universal TTML-to-SRT converter under the same name.

## Usage
```
positional arguments:
  ttml-file             TTML subtitle file
  output-file           file to write resulting SRT to

optional arguments:
  -h, --help            show this help message and exit
  -s [ms], --shift [ms]
                        shift
  -f [fps], --fps [fps]
                        frames per second (default: 23.976)
  --t-dur [sec]         target duration
  --s-dur [sec]         source duration
```

### Common use cases

Simple conversion:
```
./ttml2srt.py subtitle_from_netflix.xml > subtitle.srt
```
or
```
./ttml2srt.py subtitle_from_netflix.xml subtitle.srt
```

Shift everything forward by 2 secs:
```
./ttml2srt.py -s 2000 subtitle_from_netflix.xml > subtitle.srt
```

Convert with specific frame rate (only has an effect when input timestamps have frames):
```
./ttml2srt.py -f 25 subtitle_from_hbo_nordic.xml > subtitle.srt
```

Run tests:
```
python2 tests/test01.py
```

