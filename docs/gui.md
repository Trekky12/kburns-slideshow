# Graphical User Interface

The gui can be used by calling `kbvs.py`.
```
$ python kbvs.py
```
When you have python2 and python3 installed, you may need to run the application with `python3` instead of `python`:
```
$ python3 kbvs.py
```

## Start-Window and Menu

When starting the application the following window will be displayed:

<img src="screenshots/01_start.png" width="400px">

In the file menu a new slideshow can be created or loaded.

<img src="screenshots/02_menu_file.png" width="400px">

In the settings menu the slideshow specific and the general settings can be changed.

<img src="screenshots/03_menu_settings.png" width="400px">

## Default Settings

By selecting the menu item `General Settings` the default parameters, which are defined in `config.json`, can be changed:

<img src="screenshots/04_general_settings_window.png" width="400px">

## New Slideshow

After selecting the `New` button in the file menu a new slideshow is created:

<img src="screenshots/05_new_slideshow.png" width="400px">

## Load Slideshow

With the button `Open` a saved slideshow file (`*.json`) can be loaded. The saved file can be from the cli or from the gui.

<img src="screenshots/06_open_slideshow.png" width="400px">

## Save Slideshow

A slideshow can be saved by selecting `Save` or saved as new file by selecting `Save As..` in the file menu.

## Slideshow specific settings

After creating or loading a slideshow the slideshow specific settings can be edited in the settings menu:

<img src="screenshots/07_slideshow_settings.png" width="400px">

## Edit Slideshow

### Add slide/audio file

New slides can be added to the current slideshow by clicking on the `Add slide` button.
The selected files are then added to the current slideshow.

<img src="screenshots/08_slide_added.png" width="400px">

New audio files can be added by clicking on the `Add audio` button.

The possible filetypes are defined in the file `config.json`.

### Slide specific settings

By clicking on a slide the slide specific settings are displayed and can be changed.
It is possible to change all the slide specific settings, which are already described in the file [docs/cli.md](/docs/cli.md#slide-specific-parameters).

<img src="screenshots/09_image_slide.png" width="400px">
<img src="screenshots/10_image_slide_portrait.png" width="400px">
<img src="screenshots/11_video_slide.png" width="400px">

On image slides the kburns effect is previewed in a thumbnail so you can see which part of the image is visible on start/end of the effect.
When changing the zoom direction, zoom rate or scale mode the preview is updated.

### Audio file details

By clicking on a audio file the audio file settings are displayed.

<img src="screenshots/12_audio.png" width="400px">

### Remove slide/audio file

A slide or audio file can be removed from the slideshow by clicking the `Delete` button on the details.

### Move slide/audio file

When dragging a image or a audio file the position in the slideshow can be changed.

<img src="screenshots/13_move_slide.png" width="400px">
<img src="screenshots/14_slide_moved.png" width="400px">

## Create Video

On the bottom of the window the slideshow video duration is shown. Additionally the duration of all audio files is displayed.
To prevent no background music at the end of the video you need to make sure that the audio files duration is greater than the video duration.

If the image durations should be synced to matching audio positions the button `Sync Video to Audio` needs to be pressed.
Therefore the `aubioonset` executable is used in the background.

The resulting video can be created by pressing `Create Video`. Please note that the gui does not respond to input while creating FFmpeg creates the video.

# Credits

The screenshots are done with the following demo images:

Photo of Jökulsárlón by [Jeremy Bishop](https://unsplash.com/@jeremybishop) on [Unsplash](https://unsplash.com/photos/h7bQ8VEZtws)

Photo of Seljalandsfoss by [Andrey Andreyev](https://unsplash.com/@ludenus) on [Unsplash](https://unsplash.com/photos/dh8ONmfQyQQ)

Photo of Sunbeams shining in Iceland by [Luke Stackpoole](https://unsplash.com/@withluke) on [Unsplash](https://unsplash.com/photos/ZRsJmpt9pNI)

Video of Iceland from [coverr](https://www.coverr.co/videos/forest-waterfall-hWGAKF358u)