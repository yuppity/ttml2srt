# ttml2srt
Convert TTML subtitles used by Netflix, HBO, CMore and others to SRT format.

Note: `ttml2srt` is *not* a full-featured TTML-to-SRT converter and only works on a small subset of TTML documents. Namely, documents that follow the formats seen on the aforementioned streaming services.

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

You'll probably run into a situation where your target is playing at either slower or faster speed compared to a streaming service. You can scale timestamps to fit a source to a target by picking the same frame from both the target and source and comparing the timestamp.

Here's an example cmd for when the first piece of dialogue from a streaming service is starting two seconds behind the target audio and where a frame towards the end has a timestamp of *00:15:39* (939s) in the target and *00:16:23* (983s) in the source:
```
./ttml2srt.py -s -2000 --t-dur 939 --s-dur 983 subtitle.xml
```

Run tests:
```
python2 tests/test01.py
```

