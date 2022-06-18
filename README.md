# kburns-slideshow
kburns-slideshow allows the creation of video slideshows from images with kburns (zoom/pan) effect, videos with and without sound and background music.

![kburns-slideshow](/docs/demo/demo.gif)

<img src="/docs/screenshots/09_image_slide.png" width="400px">

## Prerequisites

kburns-slideshow is a python application and needs Python 3 installed.
The videos are generated with [FFmpeg](https://ffmpeg.org/) which is needed with the minimium Version 3. 
FFprobe (comes with FFmpeg) is used to extract the duration, width and height of input videos.

To sync the slide changes to the background music the music onsets are extracted with [aubio](https://aubio.org/).

The executables for FFmpeg, FFprobe and aubioonset, which are used, can be set in the `config.json` file.

### Run from source

#### Windows
* Download and install [Python3](https://www.python.org/downloads/)
* install Python modules
```
pip install -r requirements.txt
```
* download aubio 
  * when there should be only support for `wav` files
    * download and extract [aubio 0.4.6](https://aubio.org/download) for windows ([win64](https://aubio.org/bin/0.4.6/aubio-0.4.6-win64.zip)/[win32](https://aubio.org/bin/0.4.6/aubio-0.4.6-win32.zip)) 
  * when there should be a support for various audio files
    * download [aubio 0.4.6 with ffmpeg](https://aubio.org/download) for windows ([win64](https://aubio.org/bin/0.4.6/aubio-0.4.6-win64-ffmpeg.zip)/[win32](https://aubio.org/bin/0.4.6/aubio-0.4.6-win32-ffmpeg.zip)) and the corresponding FFmpeg 3.3.3 shared build([win64](https://archive.org/download/zeranoe/win64/shared/ffmpeg-3.3.3-win64-shared.zip)/[win32](https://archive.org/download/zeranoe/win32/shared/ffmpeg-3.3.3-win32-shared.zip))
    * extract aubio and extract the ffmpeg shared dlls from the `bin` folder of ffmpeg to the `bin` folder of aubio
* download and extract the latest version of [FFmpeg](https://www.gyan.dev/ffmpeg/builds/)
* adjusts the paths to FFmpeg (`bin/ffmpeg.exe`, `bin/ffprobe.exe`) and aubio (`bin/aubioonset.exe`) in `config.json`

#### Linux
* install Python3
```
sudo apt-get install python3 python3-pip python3-dev python3-setuptools python3-tk python3-pil python3-pil.imagetk
```

* install Python modules
```
pip3 install -r requirements.txt
```

* install ffmpeg and aubio
```
sudo apt-get install ffmpeg aubio-tools libaubio-dev libaubio-doc
```
* remove the `.exe` file extension from the paths to `ffmpeg`, `ffprobe` and `aubioonset` in `config.json`

#### MacOS

* install Python3
* install ffmpeg and aubio
```
brew install ffmpeg aubio
```
* install Python modules
```
pip install -r requirements.txt
```
* remove the `.exe` file extension from the paths to `ffmpeg`, `ffprobe` and `aubioonset` in `config.json`


### Create Executable

* install Python3 (like above) 
* install Python modules
```
pip install -r requirements.txt
pip install -r requirements-build.txt
```
* create executable
```
pyinstaller kbvs.spec
```

## Usage

### Command Line Interace
The application has a command line interface which parameters can be found at [/docs/cli.md](/docs/cli.md).

The cli can be used by calling `kbvs-cli.py` with some parameters.
```
$ python kbvs-cli.py
```
When you have python2 and python3 installed, you may need to run the application with `python3` instead of `python`:
```
$ python3 kbvs-cli.py
```

### Graphical User Interace
Additionally there is a graphical user interface which allows to create a new slideshow or load a saved slideshow file. 
The documentation can be found at [/docs/gui.md](/docs/gui.md).

The gui can be used by calling `kbvs.py`.
```
$ python kbvs.py
```
When you have python2 and python3 installed, you may need to run the application with `python3` instead of `python`:
```
$ python3 kbvs.py
```

## Notices 
When using the overlay text you need to be aware of the font specific settings. 

To use font names the FFmpeg build must be built with `--enable-libfontconfig`. This can be checked by calling `ffmpeg` and look for this attribute.

Otherwise the full path to the font needs to be specified with the parameter `font_file`.

## Transitions
It is easy possible to create custom transitions. Just place a python file in the following format in the folder [transitions](/transitions):

```python
def get(end, start, transition, i, fade_duration, config):
    filter = "%(end)s %(start)s <transition> %(transition)s" %{"end": end, "start": start, "transition": transition}
    frames = fade_duration*config["fps"]
    return filter, frames
```
The `get()` function has the following parameters:

| Parameter | Description | default |
| - | - | - |
| end | label of the end section of the previous slide  | "[v%send]" %(i-1)|
| start | label of the start section of this slide | "[v%sstart]" %(i)|
| transition | label for the transition | "[v%strans]" % (i)|
| i | slide number, which can be used for naming labels | |
| fade_duration | the transition duration (seconds) | |
| config | all global config parameters | |

The function needs to return the filter and the number of frames of the transition.

#### ffmpeg-video-slideshow-scripts transitions
I have integrated all video transitions of [ffmpeg-video-slideshow-scripts](https://github.com/tanersener/ffmpeg-video-slideshow-scripts). 

You can get the transitions by buying me a coffee from <a href="https://bmc.xyz/l/kburnstransit" target="_blank"><img src="https://bmc-cdn.nyc3.digitaloceanspaces.com/BMC-button-images/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>.

The bars and checkerboard transitions are configurable with the following global parameters:
```
    "transition_bars_count": 10,
    "transition_cell_size": 100,
```

A preview for each transition is available at [/docs/transitions.md](/docs/transitions.md).

## License
This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

The ffmpeg-video-slideshow-scripts transitions "bars_horizontal_one", "bars_horizontal_two", "bars_vertical_one", "bars_vertical_two", "checkerboard", "clock", "collapse_both", "collapse_circular", "collapse_horizontal", "collapse_vertical", "cover_horizontal_l2r", "cover_horizontal_r2l", "cover_vertical_b2t", "cover_vertical_t2b", "expand_both", "expand_circular", "expand_horizontal", "expand_vertical", "fade_in_one", "fade_in_two", "moving_bars_horizontal_l2r", "moving_bars_horizontal_r2l", "moving_bars_vertical_b2t", "moving_bars_vertical_t2b", "push_horizontal_l2r", "push_horizontal_r2l", "push_vertical_b2t", "push_vertical_t2b", "rotate_one", "sliding_bars_horizontal_l2r", "sliding_bars_horizontal_r2l", "sliding_bars_vertical_b2t", "sliding_bars_vertical_t2b", "wipe_in_horizontal_l2r", "wipe_in_horizontal_r2l", "wipe_in_vertical_b2t", "wipe_in_vertical_t2b", "wipe_out_horizontal_l2r", "wipe_out_horizontal_r2l", "wipe_out_vertical_b2t" and "wipe_out_vertical_t2b" are also licensed under the MIT license.

The ffmpeg-video-slideshow-scripts transitions "box_in_horizontal_l2r", "box_in_horizontal_r2l", "box_in_vertical_b2t", "box_in_vertical_t2b", "push_box_horizontal_l2r", "push_box_horizontal_r2l", "push_box_vertical_b2t", "push_box_vertical_t2b", "rotate_two" and "spin_blur_rotation" are licensed under the [ARTHENICA Commercial License](https://github.com/tanersener/ffmpeg-video-slideshow-scripts/blob/master/transition_video_scripts/LICENSE.Commercial.txt).

Photo of Jökulsárlón and the photo of Seljalandsfoss are under the [Unsplash license](https://unsplash.com/license)

## Credits
The project is based on [the python implementation](https://github.com/Trekky12/kburns) of [kburns by remko](https://github.com/remko/kburns) and [kburns2 by sargue](https://github.com/sargue/kburns).

A big thanks to [tanersener](https://github.com/tanersener/ffmpeg-video-slideshow-scripts) for doing the hard work of creating the various transitions.

Photo of Jökulsárlón by [Jeremy Bishop](https://unsplash.com/@jeremybishop) on [Unsplash](https://unsplash.com/photos/h7bQ8VEZtws)

Photo of Seljalandsfoss by [Andrey Andreyev](https://unsplash.com/@ludenus) on [Unsplash](https://unsplash.com/photos/dh8ONmfQyQQ)