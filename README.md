# ttml-to-srt
Convert TTML subtitles used by Netflix, HBO, CMore and others to SRT format

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
python2 ttml_srt.py subtitle_from_netflix.xml > subtitle.srt
```
or
```
python2 ttml_srt.py subtitle_from_netflix.xml subtitle.srt
```

Shift everything forward by 2 secs:
```
python2 -s 2000 ttml_srt.py subtitle_from_netflix.xml > subtitle.srt
```

Convert with specific frame rate (only has an effect when input timestamps have frames):
```
python2 -f 25 ttml_srt.py subtitle_from_hbo_nordic.xml > subtitle.srt
```
