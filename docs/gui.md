# Graphical User Interface

The gui can be used by calling `gui.py`.
```
$ python gui.py
```
When you have python2 and python3 installed, you may need to run the application with `python3` instead of `python`:
```
$ python3 gui.py
```

## Start-Window and Menu

When starting the application the following window will be displayed:
![01_start](screenshots/01_start.png)

In the file menu a new slideshow can be created or loaded.
![02_menu_file](screenshots/02_menu_file.png)

In the settings menu the slideshow specific and the general settings can be changed.
![03_menu_settings](screenshots/03_menu_settings.png)

## Default Settings

By selecting the menu item `General Settings` the default parameters, which are defined in `config.json`, can be changed:
![04_general_settings_window](screenshots/04_general_settings_window.png)

## New Slideshow

After selecting the `New` button in the file menu a new slideshow is created:

![05_new_slideshow](screenshots/05_new_slideshow.png)

## Load Slideshow

With the button `Open` a saved slideshow file (`*.json`) can be loaded. The saved file can be from the cli or from the gui.
![06_open_slideshow](screenshots/06_open_slideshow.png)

## Save Slideshow

A slideshow can be saved by selecting `Save` or saved as new file by selecting `Save As..` in the file menu.

## Slideshow specific settings

After creating or loading a slideshow the slideshow specific settings can be edited in the settings menu:
![07_slideshow_settings](screenshots/07_slideshow_settings.png)

## Edit Slideshow

### Add slide/audio file

New slides can be added to the current slideshow by clicking on the `Add slide` button.
The selected files are then added to the current slideshow.
![08_slide_added](screenshots/08_slide_added.png)

New audio files can be added by clicking on the `Add audio` button.

The possible filetypes are defined in the file `config.json`.

### Slide specific settings

By clicking on a slide the slide specific settings are displayed and can be changed.
It is possible to change all the slide specific settings, which are already described in the file [docs/cli.md](/docs/cli.md).

![09_image_slide](screenshots/09_image_slide.png)
![10_image_slide_portrait](screenshots/10_image_slide_portrait.png)
![11_video_slide](screenshots/11_video_slide.png)

On image slides the kburns effect is previewed in a thumbnail so you can see which part of the image is visible on start/end of the effect.
When changing the zoom direction, zoom rate or scale mode the preview is updated.

### Audio file details

By clicking on a audio file the audio file settings are displayed.
![12_audio](screenshots/12_audio.png)

### Remove slide/audio file

A slide or audio file can be removed from the slideshow by clicking the `Remove` button on the details.

### Move slide/audio file

When dragging a image or a audio file the position in the slideshow can be changed.
![13_move_slide](screenshots/13_move_slide.png)
![14_slide_moved](screenshots/14_slide_moved.png)

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
Photo of Sunbeams shining in Iceland by [Luke Stackpoole](https://unsplash.com/@withluke) on [Unsplash](https://unsplash.com/photos/ZRsJmpt9pNI
Video of Iceland from [coverr](https://www.coverr.co/videos/forest-waterfall-hWGAKF358u)