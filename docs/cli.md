# Command Line Usage
The application can be used by calling `kbvs-cli.py` with some parameters.
```
$ python kbvs-cli.py
```
When you have python2 and python3 installed, you may need to run the application with `python3` instead of `python`:
```
$ python3 kbvs-cli.py
```

```
usage: kbvs-cli.py [-h] [-S WIDTHxHEIGHT] [-sd DURATION] [-sdm DURATION]
               [-fd DURATION] [-ft TRANSITION] [-fps FPS] [-zd DIRECTION]
               [-zr RATE] [-sm SCALE_MODE] [-l] [-y] [-t] [-d]
               [-a [FILE [FILE ...]]] [-sy] [-i FILE [FILE ...]] [-f LIST]
               [-s FILE] [-test]
               output_file
```
The default parameters are defined in `config.json` and can be changed with the corresponding command line argument.
An output and one ore more input files (`-i <file>`) are always neccessary:
```
python kbvs-cli.py out.mp4 -i data/1.jpg data/2.jpg data/1.mp4 data/3.jpg
```

It is also possible to define an input file list with modified config parameters and input files. With an input file list it is possible to define some parameters slide specific options (e.g. a overlay text, a subtitle text, a specific transition, a slide duration, a fade duration, ...).
You can use the config file like that:
```
python kbvs-cli.py out.mp4 -f example.json
```

## Parameters

### Command Line Parameters
| Parameter | Description | possible values | default |
| - | - | - | - |
| -S / --size | output size (widthxheight) | int (width) + "x" + int (height)| 1920x1080 |
| -sd / --slide-duration | slide duration (seconds) | int | 4 |
| -sdm / --slide-duration-min | minimum slid duration (seconds), applies only when the slides duration is synced to the music | int  | 1 |
| -fd / --fade-duration | transition duration (seconds) | int | 1 |
| -ft / --fade-transition | the transition type | the names of the available transitions | "random"
| -fps / --fps | output framerate | integer | 60 |
| -zd / --zoom-direction | the zoom direction for the zoom/pan effect | "random", "top-left-in", "top-left-out", "top-center-in", "top-center-out", "top-right-in", "top-right-out", "center-left-in", "center-left-out", "center-center-in", "center-center-out", "center-right-in", "center-right-out", "bottom-left-in", "bottom-left-out", "bottom-center-in", "bottom-center-out", "bottom-right-in", "bottom-right-out" | "random" |
| -zr / --zoom-rate | the zoom rate on the zoom/pan effect | float  | 0.1 |
| -sm / --scale-mode | the scale mode for the zoom/pan effect | "pad", "crop_center", "pan" | "auto" |
| -l / --loopable | create loopable video |   | False |
| -y | overwrite output file |   | False |
| -t  / --temp | generate temporary video files which are later concatenated |   | False |
| -d  / --delete-temp | delete temporary generated video files |   | False |
| -a  / --audio | one or more background audio tracks | one ore multiple files (mp3, ogg, flac) | |
| -sy  / --sync-to-audio | sync the slides changes to the background audio (modify the slides durations) |  | False |
| --sync-titles-to-slides | sync the duration of titles to the slides durations |  | False |
| -i  / --input-files | one or more input files or input folder(s) | one ore multiple files (jpg, jpeg, png, mp4, mpg, avi)  | |
| -f  / --file-list | a JSON file with the input files | a config file which can be generated from the application / see `example.json`  | |
| -s  / --save | save the config and the slides to a JSON file | file name |  |
| -test | do not generate the video, but only test the input |  | False |

### Slide Specific Parameters
When using a JSON input file it is possible to change some values for specific slides:
* `slide_duration`
* `slide_duration_min`
* `fade_duration`
* `zoom_direction`
* `zoom_rate`
* `scale_mode`
* `transition`

```
...
        {
            "file": "1.jpg",
            "slide_duration": 5.0,
            "slide_duration_min": 1.0,
            "fade_duration": 2,
            "zoom_direction": "top-left-out",
            "zoom_rate": 0.2,
            "scale_mode": "crop_center",
            "transition": "fade"
        },
...
```

To disable the zoom/pan effect the `zoom_direction` has to be `none`. When the whole image should be visible the `scale_mode` `pad` is needed.

#### Subtitle
It is possible to define a subtitle for a slide by setting the `title` parameter in the input file list:
```
...
        {
            "file": "1.jpg",
            "title": "Slide 1"
        },
...
```
When using a MP4 output the subtitles are burned in the video. With a MKV output the subtitle is added as individual subtitle stream (default).

#### Overlay
Additionally it is possible to add a text `overlay`:
```
...
{
            "file": "1.jpg",
            "overlay_text": {
                "title": "Intro Text",
                "font": "Bauhaus 93",
                "font_size": 200,
                "duration": 2,
                "offset": 0,
                "transition_x": "left-in",
                "transition_y": "center"
            },
            "overlay_color": {
                "duration": 2,
                "offset": 0,
                "color": "black",
                "opacity": 0.8
            },
        },
...
```
A overlay can contain a color overlay and a overlaying text.

The following parameters can be set for text overlays (`overlay_text`):

| Parameter | Description | default |
| - | - | - |
| title | the text | |
| font | the font | the default FFmpeg font |
| font_file | the path to the font file, e.g. "C:\/Windows\/Fonts\/BAUHS93.TTF" | |
| font_size | the font size | 150 |
| color | the font color | white |
| duration | the duration for the overlay | 1 |
| offset | the start offset for the overlay | 0 |
| transition_x | the x-direction of the text animation which can be "center" (text is positioned on the center), "left-to-center" (text scrolls from left to the middle) or "right-to-center" (text scrolls from right to the middle) | "center" |
| transition_y | the y-direction of the text animation which can be "center" (text is positioned on the center), "top-to-bottom" (text scrolls from top to bottom) or "bottom-to-top" (text scrolls from bottom to top) | "center" |

The following parameters can be set for color overlays (`overlay_color`):

| Parameter | Description | default |
| - | - | - |
| duration | the duration for the overlay | 1 |
| offset | the start offset for the overlay | 0 |
| color | the background color | black |
| opacity | the background color opacity | 0.8 |


#### Video parameters
You can disable the audio streams of video inputs by setting `force_no_audio` to `true` on the video input slide:
```
...
        {
            "file": "1.mp4",
            "force_no_audio": true
        },
...
```

If you want only a part of a video you can define the start or end timestamp.
To use a section between second 2 and second 10 the following config is possible:
```
...
        {
            "file": "1.mp4",
            "start": 2,
            "end": 10
        },
...
```