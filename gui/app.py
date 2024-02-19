# https://stackoverflow.com/a/49681192
# https://stackoverflow.com/q/49873626


from slideshow.SlideManager import ImageSlide, VideoSlide
from slideshow.SlideManager import SlideManager
import sys
import re
import threading
import subprocess
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFilter
from tkinter.filedialog import askopenfilename, askopenfilenames, asksaveasfilename
from tkinter import messagebox
from tkinter import ttk

from .ScrollFrame import ScrollFrame
from .SettingsFrame import SettingsFrame
from .ConfigFrame import ConfigFrame
from .ProgressFrame import ProgressFrame

import os
import json

import pkgutil

import logging

logger = logging.getLogger("kburns-slideshow")


# https://stackoverflow.com/a/44633014
sys.path.append("..")

SUNKABLE_BUTTON = 'SunkableButton.TButton'


class App(tk.Tk):

    

    def __init__(self, title="", *args, **kwargs):
        super().__init__()

        self.general_title = title

        self.title(self.general_title)
        self.configure(background="Gray")

        # scale master frame to total Tk
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.geometry("800x800")  # Width x Height

        master_frame = tk.Frame(self)
        master_frame.grid(sticky=tk.NSEW)

        # scale subframes to width of master frame
        master_frame.columnconfigure(0, weight=1)
        # scroll row(s) not changable
        master_frame.rowconfigure(0, weight=0)
        master_frame.rowconfigure(1, weight=0)
        master_frame.rowconfigure(2, weight=0)
        master_frame.rowconfigure(3, weight=0)
        # scale bottom row to height of master frame
        master_frame.rowconfigure(4, weight=1)

        # Image Frame with fill parent (sticky=tk.NSEW)
        self.addSlideButton = ttk.Button(master_frame, text="Add slide", command=self.addSlide, state=tk.DISABLED)
        self.addSlideButton.grid(row=0, column=0, sticky=tk.SW)
        self.frameSlides = ScrollFrame(master_frame, 100, False)
        self.frameSlides.grid(row=1, column=0, sticky=tk.NSEW)

        # Image Frame with fill parent (sticky=tk.NSEW)
        self.addAudioButton = ttk.Button(master_frame, text="Add audio", command=self.addAudio, state=tk.DISABLED)
        self.addAudioButton.grid(row=2, column=0, sticky=tk.SW)
        self.frameAudio = ScrollFrame(master_frame, 50, False)
        self.frameAudio.grid(row=3, column=0, sticky=tk.NSEW)

        # Bottom Frame with fill parent (sticky=tk.NSEW)
        self.frameSlideSettings = ScrollFrame(master_frame, 100)
        self.frameSlideSettings.grid(row=4, column=0, sticky=tk.NSEW)

        # Buttons Frame
        frameActions = tk.Frame(master_frame, height=50)
        frameActions.grid(row=5, column=0, sticky=tk.NSEW, padx=5, pady=2)
        frameActions.columnconfigure(1, weight=1)

        labelVideoDuration = tk.Label(frameActions, text="Video Duration:")
        labelVideoDuration.grid(row=0, column=0, sticky=tk.NW)

        self.videoDurationValue = tk.StringVar()
        self.videoDurationValue.set("00:00:00")
        labelVideoDurationValue = tk.Label(frameActions, textvariable=self.videoDurationValue)
        labelVideoDurationValue.grid(row=0, column=1, sticky=tk.NW)

        labelAudioDuration = tk.Label(frameActions, text="Audio Duration:")
        labelAudioDuration.grid(row=1, column=0, sticky=tk.NW)

        self.audioDurationValue = tk.StringVar()
        self.audioDurationValue.set("00:00:00")
        labelAudioDuration = tk.Label(frameActions, textvariable=self.audioDurationValue)
        labelAudioDuration.grid(row=1, column=1, sticky=tk.NW)

        # buttonSave = tk.Button(frameActions, text="Save Configuration", command=self.saveSlideshow)
        # buttonSave.grid(row=0, column=2, rowspan = 2, sticky=tk.NW, padx=2)

        self.moveSlidesBtn = tk.IntVar()
        moveButton = ttk.Checkbutton(frameActions, text="Move slides/audio", variable=self.moveSlidesBtn)
        moveButton.grid(row=0, column=3, rowspan=2, sticky=tk.W, padx=2)

        buttonSync = tk.Button(frameActions, text="Sync Video to Audio", command=self.syncToAudio)
        buttonSync.grid(row=0, column=4, rowspan=2, sticky=tk.W, padx=2)

        buttonResetTime = tk.Button(frameActions, text="Reset slide durations", command=self.resetSlideDurations)
        buttonResetTime.grid(row=0, column=5, rowspan=2, sticky=tk.W, padx=2)

        buttonCreateVideo = tk.Button(frameActions, text="Create Video", command=self.createVideo)
        buttonCreateVideo.grid(row=0, column=6, rowspan=2, sticky=tk.W, padx=2)

        # Menu
        menubar = tk.Menu(self)
        self.filemenu = tk.Menu(menubar, tearoff=0)
        self.filemenu.add_command(label="New", command=self.newSlideshow)
        self.filemenu.add_command(label="Open", command=self.openFile)
        self.filemenu.add_command(label="Save", command=self.saveSlideshow, state="disabled")
        self.filemenu.add_command(label="Save As..", command=self.saveAs, state="disabled")
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.on_closing)
        menubar.add_cascade(label="File", menu=self.filemenu)

        self.generalmenu = tk.Menu(menubar, tearoff=0)
        self.generalmenu.add_command(label="Slideshow Settings", command=self.slideshowSettingsWindow, state="disabled")
        self.generalmenu.add_separator()
        self.generalmenu.add_command(label="General Settings", command=self.generalSettingsWindow)
        menubar.add_cascade(label="Settings", menu=self.generalmenu)

        self.config(menu=menubar)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.buttons = []
        self.buttonsAudio = []
        # https://stackoverflow.com/a/23355222
        # https://kite.com/python/docs/ttk.Style
        self.style = ttk.Style()
        self.style.configure(SUNKABLE_BUTTON, padding=2)
        self.style.map(SUNKABLE_BUTTON, background=[('pressed', 'red'), ('disabled', 'red'), ('focus', 'red')])

        self.thumbnails = []
        self.transition_choices = [package_name for importer, package_name, _ in pkgutil.iter_modules(
            [os.path.join(os.getcwd(), "transitions")])]
        self.transition_choices.append(" - None - ")
        self.zoom_direction_choices_x = ["random", "left", "center", "right"]
        self.zoom_direction_choices_y = ["random", "top", "center", "bottom"]
        self.zoom_direction_choices_z = ["random", "none", "in", "out"]
        self.scale_mode_choices = ["auto", "pad", "pan", "crop_center"]

        self.config_path = os.path.join(os.getcwd(), 'config.json')
        self.init()
        # create empty slideshow
        # self.createSlideshow()

        # Save Slide Input Fields
        self.inputTransition = tk.StringVar()
        self.inputZoomDirectionX = tk.StringVar()
        self.inputZoomDirectionY = tk.StringVar()
        self.inputZoomDirectionZ = tk.StringVar()
        self.inputScaleMode = tk.StringVar()
        self.inputPadColor = tk.StringVar()
        self.inputBlurredPadding = tk.BooleanVar()

        self.inputforceNoAudio = tk.BooleanVar()
        self.inputvideoStart = tk.StringVar()
        self.inputvideoEnd = tk.StringVar()

        self.inputDuration = tk.StringVar()
        self.inputZoomRate = tk.StringVar()
        self.inputDurationMin = tk.StringVar()
        self.inputDurationTransition = tk.StringVar()

        self.inputSubtitle = tk.StringVar()
        self.inputOverlayTextTitle = tk.StringVar()
        self.inputOverlayTextFont = tk.StringVar()
        self.inputOverlayTextFontFile = tk.StringVar()
        self.inputOverlayTextFontSize = tk.StringVar()
        self.inputOverlayTextDuration = tk.StringVar()
        self.inputOverlayTextOffset = tk.StringVar()
        self.inputOverlayTextColor = tk.StringVar()
        self.inputOverlayTextTransitionX = tk.StringVar()
        self.inputOverlayTextTransitionY = tk.StringVar()
        self.inputOverlayColorColor = tk.StringVar()
        self.inputOverlayColorDuration = tk.StringVar()
        self.inputOverlayColorOffset = tk.StringVar()
        self.inputOverlayColorOpacity = tk.StringVar()

        self.overlayTitleEntry = None
        self.padColorEntry = None
        self.bindings()
    
    def centerSlidesAroundSelected(self):
        if ((self.buttons[self.slide_selected].winfo_rootx() -self.winfo_rootx() + self.buttons[self.slide_selected].winfo_width()) / self.winfo_width() > 0.8):
            diff =  int((self.buttons[self.slide_selected].winfo_rootx() -self.winfo_rootx() + self.buttons[self.slide_selected].winfo_width()) - 0.8*self.winfo_width())
            self.frameSlides.canvas.xview("scroll", "+"+str(diff), "units")
        if ((self.buttons[self.slide_selected].winfo_rootx() -self.winfo_rootx()) / self.winfo_width() < 0.2):
            diff =  int((self.buttons[self.slide_selected].winfo_rootx() -self.winfo_rootx()) -0.2 * self.winfo_width())
            self.frameSlides.canvas.xview("scroll", str(diff), "units")

    def moveRight(self):
        if self.slide_selected < len(self.buttons) - 1:
            self.buttons.insert(self.slide_selected+1, self.buttons.pop(self.slide_selected))
            self.sm.moveSlide(self.slide_selected, self.slide_selected + 1)
            self.slide_selected += 1
            #rearrange buttons in grid
            for i, btn in enumerate(self.buttons):
                btn.grid(column=i)
            self.centerSlidesAroundSelected()
    def moveLeft(self):
        if self.slide_selected > 0:
            self.buttons.insert(self.slide_selected-1, self.buttons.pop(self.slide_selected))
            self.sm.moveSlide(self.slide_selected, self.slide_selected - 1)
            self.slide_selected -= 1
            #rearrange buttons in grid
            for i, btn in enumerate(self.buttons):
                btn.grid(column=i)
            self.centerSlidesAroundSelected()

    def selectRight(self):
        if self.slide_selected < len(self.buttons) - 1:
            self.onSlideClicked(self.slide_selected + 1)
            self.centerSlidesAroundSelected()

    def selectLeft(self):
        if self.slide_selected > 0:
            self.onSlideClicked(self.slide_selected - 1)
            self.centerSlidesAroundSelected()

    def bindings (self):
        self.bind("<Right>", lambda event: self.selectRight())
        self.bind("<Left>", lambda event: self.selectLeft())
        self.bind("s", lambda event: self.moveRight())
        self.bind("a", lambda event: self.moveLeft())
    def hasSlides(self):
        return self.sm and (len(self.sm.getSlides()) > 0 or len(self.sm.getBackgroundTracks()) > 0)

    def on_closing(self):
        if self.hasSlides():
            if messagebox.askyesno("Quit", "Do you want to quit?"):
                # Delete thumbnails
                for file in self.thumbnails:
                    if os.path.exists(file):
                        os.remove(file)
                        logger.debug("Delete %s", file)
                # Close
                self.destroy()
        else:
            self.destroy()

    def onCloseSlideshowSettings(self, toplevel):
        input_files = [slide.getObject(self.slideshow_config) for slide in self.sm.getSlides()]
        audio_files = [track.getObject() for track in self.sm.getBackgroundTracks()]
        # get new config
        self.slideshow_config.update(toplevel.getConfig())
        # close
        toplevel.destroy()
        # ask for reload
        if self.hasSlides() and \
            messagebox.askyesno("Restart",
                                "To apply general slide settings to the current slideshow, "
                                "the current slideshow needs to be reloaded. \n\nDo you want to reload the slides?"):
            self.createSlideshow(input_files, audio_files)

    def slideshowSettingsWindow(self):
        filewin = SettingsFrame(self)

        choices = {"zoom_direction_x": self.zoom_direction_choices_x,
                   "zoom_direction_y": self.zoom_direction_choices_y,
                   "zoom_direction_z": self.zoom_direction_choices_z,
                   "transition": self.transition_choices,
                   "scale_mode": self.scale_mode_choices}
        filewin.create(self.slideshow_config, choices)

        filewin.protocol("WM_DELETE_WINDOW", (lambda: self.onCloseSlideshowSettings(filewin)))

    def generalSettingsWindow(self):
        filewin = ConfigFrame(self)

        choices = {"zoom_direction_x": self.zoom_direction_choices_x,
                   "zoom_direction_y": self.zoom_direction_choices_y,
                   "zoom_direction_z": self.zoom_direction_choices_z,
                   "transition": self.transition_choices,
                   "scale_mode": self.scale_mode_choices}
        filewin.create(self.config_path, choices)

        # filewin.protocol("WM_DELETE_WINDOW", (lambda: self.onCloseTopLevel(filewin)))

    # see https://stackoverflow.com/a/39059073
    # see https://stackoverflow.com/a/51406895

    def checkEntryModification(self, event=None):
        self.slide_changed = True

        slide = self.sm.getSlides()[self.slide_selected]

        zd_x = None
        zd_y = None
        zd_z = None
        zr = None
        sc = "pad"
        if isinstance(slide, ImageSlide):
            zd_x = self.inputZoomDirectionX.get()
            if zd_x == "random":
                slide.setZoomDirectionX("random")
                zd_x = slide.direction_x
                self.inputZoomDirectionX.set(zd_x)

            zd_y = self.inputZoomDirectionY.get()
            if zd_y == "random":
                slide.setZoomDirectionY("random")
                zd_y = slide.direction_y
                self.inputZoomDirectionY.set(zd_y)

            zd_z = self.inputZoomDirectionZ.get()
            if zd_z == "random":
                slide.setZoomDirectionZ("random")
                zd_z = slide.direction_z
                self.inputZoomDirectionZ.set(zd_z)

            zr = self.inputZoomRate.get()

            sc = self.inputScaleMode.get()
            if sc == "auto":
                slide.setScaleMode("auto")
                sc = slide.scale
                self.inputScaleMode.set(sc)

        pad_c = self.inputPadColor.get()
        b_pad = self.inputBlurredPadding.get()
        photo = self.getPreviewImage(self.buttons[self.slide_selected].image_path, zd_x, zd_y, zd_z, zr, sc, pad_c, b_pad)

        if photo is not None:
            self.imageLabel.configure(image=photo)
            self.imageLabel.image = photo

        if self.overlayTitleEntry is not None:
            self.inputOverlayTextTitle.set(self.overlayTitleEntry.get('1.0', 'end-1c'))

        if self.inputBlurredPadding.get() is True:
            self.padColorEntry.config(state='disabled')
        else:
            self.padColorEntry.config(state='normal')

    def saveSlide(self):
        if self.slide_changed:
            slide = self.sm.getSlides()[self.slide_selected]

            if isinstance(slide, ImageSlide):
                slide.setDuration(float(self.inputDuration.get()))
            slide.fade_duration = float(self.inputDurationTransition.get())

            if self.inputTransition.get() != " - None - ":
                slide.transition = self.inputTransition.get()
            else:
                slide.transition = None

            if isinstance(slide, ImageSlide):
                slide.zoom_rate = float(self.inputZoomRate.get())
                slide.slide_duration_min = float(self.inputDurationMin.get())
                if slide.slide_duration_min > slide.getDuration():
                    slide.setDuration(slide.slide_duration_min)
                    self.inputDuration.set(slide.getDuration())

                slide.setZoomDirectionX(self.inputZoomDirectionX.get())
                slide.setZoomDirectionY(self.inputZoomDirectionY.get())
                slide.setZoomDirectionZ(self.inputZoomDirectionZ.get())
                slide.setScaleMode(self.inputScaleMode.get())

            if isinstance(slide, VideoSlide):
                slide.setForceNoAudio(self.inputforceNoAudio.get())
                slide.start = float(self.inputvideoStart.get()) if float(self.inputvideoStart.get()) > 0 else None
                slide.end = float(self.inputvideoEnd.get()) if float(self.inputvideoEnd.get()) > 0 else None
                slide.calculateDurationAfterTrimming()

            slide.setPadColor(self.inputPadColor.get())
            slide.setBlurredPadding(self.inputBlurredPadding.get())

            slide.title = self.inputSubtitle.get() if len(self.inputSubtitle.get()) > 0 else None

            if (len(self.inputOverlayTextTitle.get()) > 0
               or len(self.inputOverlayTextFont.get()) > 0
               or len(self.inputOverlayTextFontFile.get()) > 0
               or len(self.inputOverlayTextFontSize.get()) > 0
               or len(self.inputOverlayTextDuration.get()) > 0
               or len(self.inputOverlayTextOffset.get()) > 0
               or len(self.inputOverlayTextColor.get()) > 0
               or len(self.inputOverlayTextTransitionX.get()) > 0
               or len(self.inputOverlayTextTransitionY.get()) > 0):
                overlay_text = {}
                if len(self.inputOverlayTextTitle.get()) > 0:
                    overlay_text["title"] = self.inputOverlayTextTitle.get()
                if len(self.inputOverlayTextFont.get()) > 0:
                    overlay_text["font"] = self.inputOverlayTextFont.get()
                if len(self.inputOverlayTextFontFile.get()) > 0:
                    overlay_text["font_file"] = self.inputOverlayTextFontFile.get()
                if len(self.inputOverlayTextFontSize.get()) > 0:
                    overlay_text["font_size"] = float(self.inputOverlayTextFontSize.get())
                if len(self.inputOverlayTextDuration.get()) > 0:
                    overlay_text["duration"] = float(self.inputOverlayTextDuration.get())
                if len(self.inputOverlayTextOffset.get()) > 0:
                    overlay_text["offset"] = float(self.inputOverlayTextOffset.get())
                if len(self.inputOverlayTextColor.get()) > 0:
                    overlay_text["color"] = self.inputOverlayTextColor.get()
                if len(self.inputOverlayTextTransitionX.get()) > 0:
                    overlay_text["transition_x"] = self.inputOverlayTextTransitionX.get()
                if len(self.inputOverlayTextTransitionY.get()) > 0:
                    overlay_text["transition_y"] = self.inputOverlayTextTransitionY.get()

                slide.overlay_text = overlay_text if overlay_text else None

            if (len(self.inputOverlayColorColor.get()) > 0
               or len(self.inputOverlayColorOpacity.get()) > 0
               or len(self.inputOverlayColorDuration.get()) > 0
               or len(self.inputOverlayColorOffset.get()) > 0):
                overlay_color = {}
                if len(self.inputOverlayColorColor.get()) > 0:
                    overlay_color["color"] = self.inputOverlayColorColor.get()
                if len(self.inputOverlayColorOpacity.get()) > 0:
                    overlay_color["opacity"] = float(self.inputOverlayColorOpacity.get())
                if len(self.inputOverlayColorDuration.get()) > 0:
                    overlay_color["duration"] = float(self.inputOverlayColorDuration.get())
                if len(self.inputOverlayColorOffset.get()) > 0:
                    overlay_color["offset"] = float(self.inputOverlayColorOffset.get())

                slide.overlay_color = overlay_color if overlay_color else None

            self.slide_changed = False

            # Recalculate video duration
            duration = self.sm.getTotalDuration()
            self.videoDurationValue.set(self.formatDuration(duration))

            # Recalculate audio duration
            duration = self.sm.getAudioDuration() + self.sm.getVideoAudioDuration()
            self.audioDurationValue.set(self.formatDuration(duration))

    # see https://stackoverflow.com/a/46670374
    def validateDigit(self, P):
        if not P:
            return True
        try:
            float(P)
            return True
        except ValueError:
            return False

    def loadConfig(self):
        self.slideshow_config = {}
        if os.path.exists(self.config_path):
            with open(self.config_path) as config_file:
                self.slideshow_config = json.load(config_file)

    def init(self):
        self.filename = None
        self.title(self.general_title)
        self.input_files = []
        self.audio_files = []
        self.slide_selected = None
        self.audio_selected = None
        self.slide_changed = False
        self.sm = None
        self.loadConfig()

    def newSlideshow(self):
        if self.hasSlides() and messagebox.askyesno("New", "Do you want to save the current slideshow?"):
            self.saveSlideshow()
        self.init()
        self.createSlideshow()

    def openFile(self):
        if self.hasSlides() and messagebox.askyesno("New", "Do you want to save the current slideshow?"):
            self.saveSlideshow()

        self.init()
        ftypes = [
            ('Slideshow config', '*.json')
        ]
        self.filename = askopenfilename(filetypes=ftypes)
        try:
            with open(self.filename) as f:
                file_content = json.load(f)

                if "config" in file_content:
                    self.slideshow_config.update(file_content["config"])
                    logger.debug("overwrite config")

                if "slides" in file_content:
                    input_files = file_content["slides"]
                    logger.debug("get slides")

                if "audio" in file_content:
                    audio_files = file_content["audio"]
                    logger.debug("get audio")

            res = self.createSlideshow(input_files, audio_files)
            if res:
                self.title("%s (%s)" % (self.general_title, self.filename))
        except Exception as e:
            print("file must be a JSON file")
            print(e)
            logger.error("file %s must be a JSON file", self.filename)

    def createSlideshow(self, input_files=[], audio_files=[]):
        self.resetGUI()
        self.generalmenu.entryconfig("Slideshow Settings", state="disabled")

        try:
            self.sm = SlideManager(self.slideshow_config, input_files, audio_files)
            self.loadSlideshowImagesRow()
            self.loadSlideshowAudioRow()
            self.generalmenu.entryconfig("Slideshow Settings", state="normal")
            self.filemenu.entryconfig("Save", state="normal")
            self.filemenu.entryconfig("Save As..", state="normal")
        except Exception as e:
            logger.error("Could not initiate Slideshow Manager, Error: %s", e)
            messagebox.showerror(
                "Error", "Could not initiate Slideshow Manager.\nPlease check general Settings.\n\nError: %s" % (e))
            return False

        return True

    def resetGUI(self):
        self.frameSlides.clear()
        self.frameAudio.clear()
        self.frameSlideSettings.clear()
        self.addSlideButton["state"] = tk.DISABLED
        self.addAudioButton["state"] = tk.DISABLED

    def loadSlideshowImagesRow(self):
        canvas2 = self.frameSlides.getCanvas()

        images_frame = tk.Frame(canvas2, padx=5, pady=5)

        basewidth = 150

        self.buttons = []
        i = 0
        for i, slide in enumerate(self.sm.getSlides()):
            img_path = slide.file
            if isinstance(slide, VideoSlide):
                img_path = os.path.join(self.sm.tempFileFolder, 'thumbnail_%s.jpg' % (i))
                si = None
                if hasattr(subprocess, 'STARTUPINFO'):
                    si = subprocess.STARTUPINFO()
                    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                subprocess.check_output([
                    self.slideshow_config["ffmpeg"],
                    '-i', slide.file,
                    '-ss', '00:00:00.000',
                    '-vframes', '1',
                    '-hide_banner',
                    '-v', 'quiet',
                    '-y', img_path
                ],
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    startupinfo=si
                )
                self.thumbnails.append(img_path)

            # https://stackoverflow.com/a/44978329
            img = Image.open(img_path)

            img.thumbnail((basewidth, basewidth / 2))

            photo = ImageTk.PhotoImage(img)

            # https://stackoverflow.com/a/45733411
            # https://stackoverflow.com/questions/50787864/how-do-i-make-a-tkinter-button-in-an-list-of-buttons-return-its-index#comment88609106_50787933
            # command=lambda c=i: self.onSlideClicked(c),
            b = ttk.Button(images_frame, image=photo, style=SUNKABLE_BUTTON)
            b.image = photo  # keep a reference
            b.grid(row=0, column=i, sticky=tk.NSEW)

            # save reference to image path
            b.image_path = img_path

            b.bind("<Button-1>", self.buttonDragStart)
            b.bind("<B1-Motion>", self.buttonDragMotion)
            b.bind("<ButtonRelease-1>", self.buttonDragStopSlide)

            self.buttons.append(b)

        # addButton = ttk.Button(images_frame, text="Add slide", command=self.addSlide)
        # addButton.grid(row=0, column=i + 1, sticky=tk.SW)

        self.addSlideButton["state"] = tk.NORMAL

        self.frameSlides.addFrame(images_frame)
        duration = self.sm.getTotalDuration()
        self.videoDurationValue.set(self.formatDuration(duration))

        self.slide_selected = None

    def onSlideClicked(self, button_id):
        for btn in self.buttons:
            btn.state(['!pressed', '!disabled', '!focus'])

        for btn in self.buttonsAudio:
            btn.state(['!pressed', '!disabled'])

        self.buttons[button_id].state(['pressed', 'disabled'])

        # save previous slide
        self.saveSlide()

        self.slide_selected = button_id
        slide = self.sm.getSlides()[button_id]

        vcmd = (self.register(self.validateDigit))

        self.frameSlideSettings.clear()
        canvas3 = self.frameSlideSettings.getCanvas()

        optionsFrame = tk.Frame(canvas3, padx=5, pady=5)
        # optionsFrame.grid(sticky=tk.NSEW)
        optionsFrame.columnconfigure(0, weight=0)
        optionsFrame.columnconfigure(1, weight=1)

        generalframe = tk.LabelFrame(optionsFrame, text="General")
        generalframe.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)  # columnspan=2,

        buttonsFrame = tk.Frame(optionsFrame)
        buttonsFrame.grid(row=1, columnspan=3, sticky=tk.NW, padx=4, pady=4)

        # buttonSaveSlide = tk.Button(buttonsFrame, text="Save", command=(lambda: self.saveSlide()))
        # buttonSaveSlide.pack()
        buttonDeleteSlide = tk.Button(buttonsFrame, text="Remove", command=(lambda: self.deleteSlide()))
        buttonDeleteSlide.pack()

        fileLabel = tk.Label(generalframe, text="File")
        fileLabel.grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        fileEntry = tk.Entry(generalframe, width=70)
        fileEntry.insert(0, slide.file)
        fileEntry.configure(state='readonly')
        fileEntry.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)

        transitionframe = tk.LabelFrame(optionsFrame, text="Transition")
        transitionframe.grid(row=2, column=0, sticky=tk.NSEW, padx=5, pady=5)

        if slide.transition is not None:
            self.inputTransition.set(slide.transition)
        else:
            self.inputTransition.set(" - None - ")
        transitionLabel = tk.Label(transitionframe, text="Transition")
        transitionLabel.grid(row=0, column=0, sticky=tk.E, padx=4, pady=4)
        transitionCombo = ttk.Combobox(
            transitionframe, values=self.transition_choices, width=30, textvariable=self.inputTransition)
        transitionCombo.grid(row=0, column=1, sticky=tk.E, padx=4, pady=4)
        transitionCombo.bind("<<ComboboxSelected>>", self.checkEntryModification)

        self.inputDurationTransition.set(slide.fade_duration)
        durationFadeLabel = tk.Label(transitionframe, text="Duration")
        durationFadeLabel.grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
        durationFadeEntry = tk.Entry(transitionframe, validate='all', validatecommand=(
            vcmd, '%P'), textvariable=self.inputDurationTransition)
        durationFadeEntry.grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)
        durationFadeEntry.bind("<KeyRelease>", self.checkEntryModification)

        if isinstance(slide, ImageSlide):
            imageframe = tk.LabelFrame(optionsFrame, text="Image Options")
            imageframe.grid(row=3, column=0, sticky=tk.NSEW, padx=5, pady=5)

            self.inputDurationMin.set(slide.slide_duration_min)
            durationMinLabel = tk.Label(imageframe, text="Duration (min)")
            durationMinLabel.grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
            durationMinEntry = tk.Entry(imageframe, validate='all', validatecommand=(
                vcmd, '%P'), textvariable=self.inputDurationMin)
            durationMinEntry.grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)
            durationMinEntry.bind("<KeyRelease>", self.checkEntryModification)

            self.inputZoomDirectionX.set(slide.getZoomDirectionX())
            zoomDirectionXLabel = tk.Label(imageframe, text="Zoom Direction X")
            zoomDirectionXLabel.grid(row=2, column=0, sticky=tk.W, padx=4, pady=4)
            zoomDirectionXCombo = ttk.Combobox(
                imageframe, values=self.zoom_direction_choices_x, textvariable=self.inputZoomDirectionX)
            zoomDirectionXCombo.grid(row=2, column=1, sticky=tk.E, padx=4, pady=4)
            zoomDirectionXCombo.bind("<<ComboboxSelected>>", self.checkEntryModification)

            self.inputZoomDirectionY.set(slide.getZoomDirectionY())
            zoomDirectionYLabel = tk.Label(imageframe, text="Zoom Direction Y")
            zoomDirectionYLabel.grid(row=3, column=0, sticky=tk.W, padx=4, pady=4)
            zoomDirectionYCombo = ttk.Combobox(
                imageframe, values=self.zoom_direction_choices_y, textvariable=self.inputZoomDirectionY)
            zoomDirectionYCombo.grid(row=3, column=1, sticky=tk.E, padx=4, pady=4)
            zoomDirectionYCombo.bind("<<ComboboxSelected>>", self.checkEntryModification)

            self.inputZoomDirectionZ.set(slide.getZoomDirectionZ())
            zoomDirectionZLabel = tk.Label(imageframe, text="Zoom Direction Z")
            zoomDirectionZLabel.grid(row=4, column=0, sticky=tk.W, padx=4, pady=4)
            zoomDirectionZCombo = ttk.Combobox(
                imageframe, values=self.zoom_direction_choices_z, textvariable=self.inputZoomDirectionZ)
            zoomDirectionZCombo.grid(row=4, column=1, sticky=tk.E, padx=4, pady=4)
            zoomDirectionZCombo.bind("<<ComboboxSelected>>", self.checkEntryModification)

            self.inputZoomRate.set(slide.zoom_rate)
            zoomRateLabel = tk.Label(imageframe, text="Zoom Rate")
            zoomRateLabel.grid(row=5, column=0, sticky=tk.W, padx=4, pady=4)
            zoomRateEntry = tk.Entry(imageframe, validate='all', validatecommand=(
                vcmd, '%P'), textvariable=self.inputZoomRate)
            zoomRateEntry.grid(row=5, column=1, sticky=tk.W, padx=4, pady=4)
            zoomRateEntry.bind("<KeyRelease>", self.checkEntryModification)

            self.inputScaleMode.set(slide.scale)
            scaleModeLabel = tk.Label(imageframe, text="Scale Mode")
            scaleModeLabel.grid(row=6, column=0, sticky=tk.W, padx=4, pady=4)
            scaleModeCombo = ttk.Combobox(imageframe, values=self.scale_mode_choices, textvariable=self.inputScaleMode)
            scaleModeCombo.grid(row=6, column=1, sticky=tk.W, padx=4, pady=4)
            scaleModeCombo.bind("<<ComboboxSelected>>", self.checkEntryModification)

        if isinstance(slide, VideoSlide):
            videoframe = tk.LabelFrame(optionsFrame, text="Video Options")
            videoframe.grid(row=3, column=0, sticky=tk.NSEW, padx=5, pady=5)

            self.inputforceNoAudio.set(slide.force_no_audio)
            forceNoAudioLabel = tk.Label(videoframe, text="No Audio")
            forceNoAudioLabel.grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
            forceNoAudioCheckBox = tk.Checkbutton(
                videoframe, var=self.inputforceNoAudio)
            forceNoAudioCheckBox.grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)
            forceNoAudioCheckBox.bind("<ButtonRelease>", self.checkEntryModification)

            self.inputvideoStart.set(slide.start if slide.start is not None else -1)
            videoStartLabel = tk.Label(videoframe, text="Video Start")
            videoStartLabel.grid(row=2, column=0, sticky=tk.W, padx=4, pady=4)
            videoStartEntry = tk.Entry(videoframe, textvariable=self.inputvideoStart)
            videoStartEntry.grid(row=2, column=1, sticky=tk.W, padx=4, pady=4)
            videoStartEntry.bind("<KeyRelease>", self.checkEntryModification)

            self.inputvideoEnd.set(slide.end if slide.end is not None else -1)
            videoEndLabel = tk.Label(videoframe, text="Video End")
            videoEndLabel.grid(row=3, column=0, sticky=tk.W, padx=4, pady=4)
            videoEndEntry = tk.Entry(videoframe, textvariable=self.inputvideoEnd)
            videoEndEntry.grid(row=3, column=1, sticky=tk.W, padx=4, pady=4)
            videoEndEntry.bind("<KeyRelease>", self.checkEntryModification)

        if isinstance(slide, ImageSlide):
            durationFrame = imageframe
        else:
            durationFrame = videoframe
        self.inputDuration.set(slide.getDuration())
        durationLabel = tk.Label(durationFrame, text="Duration")
        durationLabel.grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        durationEntry = tk.Entry(durationFrame, validate='all', validatecommand=(
            vcmd, '%P'), textvariable=self.inputDuration)
        durationEntry.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)
        durationEntry.bind("<KeyRelease>", self.checkEntryModification)

        if isinstance(slide, VideoSlide):
            self.inputDuration.set(slide.video_duration)
            durationEntry.configure(state="disabled")

        paddingFrame = tk.LabelFrame(optionsFrame, text="Padding Options")
        paddingFrame.grid(row=4, column=0, sticky=tk.NSEW, padx=5, pady=5)

        self.inputPadColor.set(slide.pad_color)
        padColorLabel = tk.Label(paddingFrame, text="Padding Background Color")
        padColorLabel.grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        self.padColorEntry = tk.Entry(paddingFrame, validate='all', validatecommand=(
            vcmd, '%P'), textvariable=self.inputPadColor)
        self.padColorEntry.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)
        self.padColorEntry.bind("<KeyRelease>", self.checkEntryModification)

        self.inputBlurredPadding.set(slide.blurred_padding)
        blurredPaddingLabel = tk.Label(paddingFrame, text="Blurred padding (no color)")
        blurredPaddingLabel.grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
        blurredPaddingCheckBox = tk.Checkbutton(
            paddingFrame, var=self.inputBlurredPadding, command=self.checkEntryModification)
        blurredPaddingCheckBox.grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)
        blurredPaddingCheckBox.bind("<ButtonRelease>", self.checkEntryModification)

        if self.inputBlurredPadding.get() is True:
            self.padColorEntry.config(state='disabled')
        else:
            self.padColorEntry.config(state='normal')

        subtitleFrame = tk.LabelFrame(optionsFrame, text="Subtitle")
        subtitleFrame.grid(row=5, column=0, sticky=tk.NSEW, padx=5, pady=5)

        self.inputSubtitle.set(slide.title if slide.title else "")
        subtitleLabel = tk.Label(subtitleFrame, text="Subtitle")
        subtitleLabel.grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        subtitleEntry = tk.Entry(subtitleFrame, textvariable=self.inputSubtitle, width=50)
        subtitleEntry.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)
        subtitleEntry.bind("<KeyRelease>", self.checkEntryModification)

        overlayFrameColor = tk.LabelFrame(optionsFrame, text="Color Overlay")
        overlayFrameColor.grid(row=6, column=0, sticky=tk.NSEW, padx=5, pady=5)

        self.inputOverlayColorDuration.set(
            slide.overlay_color["duration"] if slide.overlay_color and "duration" in slide.overlay_color else "")
        overlayColorDurationLabel = tk.Label(overlayFrameColor, text="Duration")
        overlayColorDurationLabel.grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        overlayColorDurationEntry = tk.Entry(overlayFrameColor, validate='all', validatecommand=(
            vcmd, '%P'), textvariable=self.inputOverlayColorDuration)
        overlayColorDurationEntry.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)
        overlayColorDurationEntry.bind("<KeyRelease>", self.checkEntryModification)

        self.inputOverlayColorOffset.set(
            slide.overlay_color["offset"] if slide.overlay_color and "offset" in slide.overlay_color else 0)
        overlayColorOffsetLabel = tk.Label(overlayFrameColor, text="Offset")
        overlayColorOffsetLabel.grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
        overlayColoOffsetEntry = tk.Entry(overlayFrameColor, validate='all', validatecommand=(
            vcmd, '%P'), textvariable=self.inputOverlayColorOffset)
        overlayColoOffsetEntry.grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)
        overlayColoOffsetEntry.bind("<KeyRelease>", self.checkEntryModification)

        self.inputOverlayColorColor.set(
            slide.overlay_color["color"] if slide.overlay_color and "color" in slide.overlay_color else "black")
        overlayColorColorLabel = tk.Label(overlayFrameColor, text="Color")
        overlayColorColorLabel.grid(row=2, column=0, sticky=tk.W, padx=4, pady=4)
        overlayColorColorEntry = tk.Entry(overlayFrameColor, textvariable=self.inputOverlayColorColor, width=50)
        overlayColorColorEntry.grid(row=2, column=1, sticky=tk.W, padx=4, pady=4)
        overlayColorColorEntry.bind("<KeyRelease>", self.checkEntryModification)

        self.inputOverlayColorOpacity.set(
            slide.overlay_color["opacity"] if slide.overlay_color and "opacity" in slide.overlay_color else 0.8)
        overlayColorOpacityLabel = tk.Label(overlayFrameColor, text="Opacity")
        overlayColorOpacityLabel.grid(row=3, column=0, sticky=tk.W, padx=4, pady=4)
        overlayColorOpacityEntry = tk.Entry(overlayFrameColor, textvariable=self.inputOverlayColorOpacity, width=50)
        overlayColorOpacityEntry.grid(row=3, column=1, sticky=tk.W, padx=4, pady=4)
        overlayColorOpacityEntry.bind("<KeyRelease>", self.checkEntryModification)

        overlayFrameText = tk.LabelFrame(optionsFrame, text="Text Overlay")
        overlayFrameText.grid(row=7, column=0, sticky=tk.NSEW, padx=5, pady=5)

        self.inputOverlayTextTitle.set(
            slide.overlay_text["title"] if slide.overlay_text and "title" in slide.overlay_text else "")
        overlayTitleLabel = tk.Label(overlayFrameText, text="Title")
        overlayTitleLabel.grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        self.overlayTitleEntry = tk.Text(overlayFrameText, width=41, height=2)
        self.overlayTitleEntry.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)
        self.overlayTitleEntry.bind("<KeyRelease>", self.checkEntryModification)
        self.overlayTitleEntry.insert('1.0', self.inputOverlayTextTitle.get())

        self.inputOverlayTextFont.set(
            slide.overlay_text["font"] if slide.overlay_text and "font" in slide.overlay_text else "")
        overlayFontLabel = tk.Label(overlayFrameText, text="Font")
        overlayFontLabel.grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
        overlayFontEntry = tk.Entry(overlayFrameText, textvariable=self.inputOverlayTextFont, width=50)
        overlayFontEntry.grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)
        overlayFontEntry.bind("<KeyRelease>", self.checkEntryModification)

        self.inputOverlayTextFontFile.set(
            slide.overlay_text["font_file"] if slide.overlay_text and "font_file" in slide.overlay_text else "")
        overlayFontFileLabel = tk.Label(overlayFrameText, text="Font file")
        overlayFontFileLabel.grid(row=2, column=0, sticky=tk.W, padx=4, pady=4)
        overlayFontFileEntry = tk.Entry(overlayFrameText, textvariable=self.inputOverlayTextFontFile, width=50)
        overlayFontFileEntry.grid(row=2, column=1, sticky=tk.W, padx=4, pady=4)
        overlayFontFileEntry.bind("<KeyRelease>", self.checkEntryModification)

        self.inputOverlayTextFontSize.set(
            slide.overlay_text["font_size"] if slide.overlay_text and "font_size" in slide.overlay_text else "")
        overlayFontSizeLabel = tk.Label(overlayFrameText, text="Font size")
        overlayFontSizeLabel.grid(row=3, column=0, sticky=tk.W, padx=4, pady=4)
        overlayFontSizeEntry = tk.Entry(overlayFrameText, validate='all', validatecommand=(
            vcmd, '%P'), textvariable=self.inputOverlayTextFontSize)
        overlayFontSizeEntry.grid(row=3, column=1, sticky=tk.W, padx=4, pady=4)
        overlayFontSizeEntry.bind("<KeyRelease>", self.checkEntryModification)

        self.inputOverlayTextColor.set(
            slide.overlay_text["color"] if slide.overlay_text and "color" in slide.overlay_text else "white")
        overlayFontColorLabel = tk.Label(overlayFrameText, text="Color")
        overlayFontColorLabel.grid(row=4, column=0, sticky=tk.W, padx=4, pady=4)
        overlayFontColorEntry = tk.Entry(overlayFrameText, textvariable=self.inputOverlayTextColor, width=50)
        overlayFontColorEntry.grid(row=4, column=1, sticky=tk.W, padx=4, pady=4)
        overlayFontColorEntry.bind("<KeyRelease>", self.checkEntryModification)

        self.inputOverlayTextDuration.set(
            slide.overlay_text["duration"] if slide.overlay_text and "duration" in slide.overlay_text else "")
        overlayFontDurationLabel = tk.Label(overlayFrameText, text="Duration")
        overlayFontDurationLabel.grid(row=5, column=0, sticky=tk.W, padx=4, pady=4)
        overlayFontDurationEntry = tk.Entry(overlayFrameText, validate='all', validatecommand=(
            vcmd, '%P'), textvariable=self.inputOverlayTextDuration)
        overlayFontDurationEntry.grid(row=5, column=1, sticky=tk.W, padx=4, pady=4)
        overlayFontDurationEntry.bind("<KeyRelease>", self.checkEntryModification)

        self.inputOverlayTextOffset.set(
            slide.overlay_text["offset"] if slide.overlay_text and "offset" in slide.overlay_text else 0)
        overlayFonOffsetLabel = tk.Label(overlayFrameText, text="Offset")
        overlayFonOffsetLabel.grid(row=6, column=0, sticky=tk.W, padx=4, pady=4)
        overlayFontOffsetEntry = tk.Entry(overlayFrameText, validate='all', validatecommand=(
            vcmd, '%P'), textvariable=self.inputOverlayTextOffset)
        overlayFontOffsetEntry.grid(row=6, column=1, sticky=tk.W, padx=4, pady=4)
        overlayFontOffsetEntry.bind("<KeyRelease>", self.checkEntryModification)

        self.inputOverlayTextTransitionX.set(
            slide.overlay_text["transition_x"] if slide.overlay_text and "transition_x" in slide.overlay_text else "center")
        overlayTransitionXLabel = tk.Label(overlayFrameText, text="Transition X Direction")
        overlayTransitionXLabel.grid(row=7, column=0, sticky=tk.W, padx=4, pady=4)
        overlayTransitionXCombo = ttk.Combobox(overlayFrameText, values=["center", "right-to-center", "left-to-center"],
                                               textvariable=self.inputOverlayTextTransitionX)
        overlayTransitionXCombo.grid(row=7, column=1, sticky=tk.W, padx=4, pady=4)
        overlayTransitionXCombo.bind("<<ComboboxSelected>>", self.checkEntryModification)

        self.inputOverlayTextTransitionY.set(
            slide.overlay_text["transition_y"] if slide.overlay_text and "transition_y" in slide.overlay_text else "center")
        overlayTransitionYLabel = tk.Label(overlayFrameText, text="Transition Y Direction")
        overlayTransitionYLabel.grid(row=8, column=0, sticky=tk.W, padx=4, pady=4)
        overlayTransitionYCombo = ttk.Combobox(overlayFrameText, values=["center", "top-to-bottom", "bottom-to-top"],
                                               textvariable=self.inputOverlayTextTransitionY)
        overlayTransitionYCombo.grid(row=8, column=1, sticky=tk.W, padx=4, pady=4)
        overlayTransitionYCombo.bind("<<ComboboxSelected>>", self.checkEntryModification)

        # Right column (image preview)
        imageframe = tk.LabelFrame(optionsFrame, text="Image")
        imageframe.grid(row=0, column=1, rowspan=5, sticky=tk.NW, padx=5, pady=5)

        # get image path from button and create "bigger" preview
        zd_x = slide.getZoomDirectionX() if isinstance(slide, ImageSlide) else None
        zd_y = slide.getZoomDirectionY() if isinstance(slide, ImageSlide) else None
        zd_z = slide.getZoomDirectionZ() if isinstance(slide, ImageSlide) else None
        zr = slide.zoom_rate if isinstance(slide, ImageSlide) else None
        sc = slide.scale if isinstance(slide, ImageSlide) else "pad"
        pad_c = slide.pad_color
        b_pad = slide.blurred_padding
        photo = self.getPreviewImage(self.buttons[button_id].image_path, zd_x, zd_y, zd_z, zr, sc, pad_c, b_pad)

        if photo is not None:
            self.imageLabel = tk.Label(imageframe, image=photo)
            self.imageLabel.grid(row=0, column=0, sticky=tk.E, padx=4, pady=4)
            # keep a reference
            self.imageLabel.image = photo

        self.frameSlideSettings.addFrame(optionsFrame, tk.NW)

    def getPreviewImage(self, img_path, zoom_direction_x=None, zoom_direction_y=None, zoom_direction_z=None,
                        zoom_rate=None, scale=None, pad_color='black', blurred_padding=False):
        output_ratio = float(self.slideshow_config["output_width"]) / float(self.slideshow_config["output_height"])
        thumb_width = 800
        thumb_height = int(thumb_width / output_ratio)

        slideImage = Image.open(img_path)
        slideImage_width, slideImage_height = slideImage.size
        slideImage_ratio = slideImage_width / slideImage_height

        slidethumb_width, slidethumb_height = [thumb_width, thumb_height]
        if scale == "crop_center":
            if slideImage_ratio < output_ratio:
                slidethumb_width, slidethumb_height = [thumb_width, int(thumb_width / slideImage_ratio)]
            else:
                slidethumb_width, slidethumb_height = [int(thumb_height * slideImage_ratio), thumb_height]
        elif scale == "pad" or scale == "pan":
            if slideImage_ratio > output_ratio:
                slidethumb_width, slidethumb_height = [thumb_width, int(thumb_width / slideImage_ratio)]
            else:
                slidethumb_width, slidethumb_height = [int(thumb_height * slideImage_ratio), thumb_height]

        slideImage.thumbnail((slidethumb_width, slidethumb_height))

        try:
            if pad_color == "#00000000":
                pad_color = "#000000FF"
            img = Image.new('RGBA', (thumb_width, thumb_height), color=pad_color)
        except ValueError:
            logger.debug("Error creating preview image, wrong color name")
            return None

        if blurred_padding:
            blurredImage = Image.open(img_path)
            blurredImage = blurredImage.resize((thumb_width, thumb_height))
            blurredImage = blurredImage.filter(ImageFilter.BoxBlur(20))
            img.paste(blurredImage)

        thumb_x = int((thumb_width - slidethumb_width) / 2)
        thumb_y = int((thumb_height - slidethumb_height) / 2)
        img.paste(slideImage, (thumb_x, thumb_y))

        # transition preview
        if zoom_direction_x is not None and zoom_direction_y is not None and zoom_direction_z is not None \
           and zoom_direction_z != "none" and zoom_rate is not None:
            draw = ImageDraw.Draw(img)
            # [thumb_width, int(thumb_width/output_ratio)]
            width, height = img.size
            output_width = width
            output_height = int(output_width / output_ratio)
            x1 = 0
            y1 = 0
            x2 = 0
            y2 = 0

            z_initial = 1
            z_step = float(zoom_rate)
            if scale == "pan":
                z_initial = slideImage_ratio / \
                    output_ratio if slideImage_ratio > output_ratio else output_ratio / slideImage_ratio
                z_step = z_step * z_initial

            scale_factor = 1 / (z_initial + z_step)

            if zoom_direction_x == "left":
                x1 = 0
            elif zoom_direction_x == "right":
                x1 = width - width * scale_factor
            elif zoom_direction_x == "center":
                x1 = (width - output_width * scale_factor) / 2

            if zoom_direction_y == "top":
                y1 = 0
            elif zoom_direction_y == "bottom":
                y1 = height - output_height * scale_factor
            elif zoom_direction_y == "center":
                y1 = (height - output_height * scale_factor) / 2

            x2 = x1 + output_width * scale_factor
            y2 = y1 + output_height * scale_factor

            # adjust coordinates for panning
            if scale == "pan":
                if zoom_direction_x == "left":
                    x1 = x1 + thumb_x
                    x2 = x2 + thumb_x
                elif zoom_direction_x == "right":
                    x1 = x1 - thumb_x
                    x2 = x2 - thumb_x

                if zoom_direction_y == "top":
                    y1 = y1 + thumb_y
                    y2 = y2 + thumb_y
                elif zoom_direction_y == "bottom":
                    y1 = y1 - thumb_y
                    y2 = y2 - thumb_y
            draw.rectangle([(x1, y1), (x2, y2)], outline="red", width=3)

            # draw initial rectangle on panning
            if scale == "pan":
                # horizontal image in landscape output
                if slideImage_ratio < output_ratio:
                    img_w = slidethumb_width
                    img_h = slidethumb_width / output_ratio

                    if zoom_direction_y == "top":
                        x0_1 = thumb_x
                        y0_1 = height - thumb_y - img_h
                        x0_2 = thumb_x + img_w
                        y0_2 = height - thumb_y
                    elif zoom_direction_y == "bottom":
                        x0_1 = thumb_x
                        y0_1 = thumb_y
                        x0_2 = thumb_x + img_w
                        y0_2 = thumb_y + img_h
                    elif zoom_direction_y == "center":
                        x0_1 = thumb_x
                        y0_1 = (height - thumb_y - img_h) / 2
                        x0_2 = thumb_x + img_w
                        y0_2 = y0_1 + img_h
                else:
                    img_w = slidethumb_height * output_ratio
                    img_h = slidethumb_height

                    if zoom_direction_x == "left":
                        x0_1 = width - thumb_x - img_w
                        y0_1 = height - thumb_y
                        x0_2 = width - thumb_x
                        y0_2 = height - thumb_y - img_h
                    elif zoom_direction_x == "right":
                        x0_1 = thumb_x
                        y0_1 = height - thumb_y
                        x0_2 = thumb_x + img_w
                        y0_2 = height - thumb_y - img_h
                    elif zoom_direction_x == "center":
                        x0_1 = (width - thumb_x - img_w) / 2
                        y0_1 = thumb_y
                        x0_2 = x0_1 + img_w
                        y0_2 = thumb_y + img_h
                draw.rectangle([(x0_1, y0_1), (x0_2, y0_2)], outline="red", width=3)

            # direction
            if scale == "pad" or scale == "crop_center":
                top_left = (0, 0)
                top_right = (width, 0)
                bottom_left = (0, height)
                bottom_right = (width, height)
            elif scale == "pan":
                top_left = (thumb_x, thumb_y)
                top_right = (width - thumb_x, thumb_y)
                bottom_left = (thumb_x, height - thumb_y)
                bottom_right = (width - thumb_x, height - thumb_y)

                if ((zoom_direction_y == "center" and slideImage_ratio < output_ratio)
                   or (zoom_direction_x == "center" and not slideImage_ratio < output_ratio)):
                    top_left = (x0_1, y0_1)
                    top_right = (x0_2, y0_1)
                    bottom_left = (x0_1, y0_2)
                    bottom_right = (x0_2, y0_2)

            if zoom_direction_y == "top":
                if zoom_direction_x == "left":
                    draw.line([(x2, y2), bottom_right], fill="red", width=3)
                elif zoom_direction_x == "right":
                    draw.line([(x1, y2), bottom_left], fill="red", width=3)
                elif zoom_direction_x == "center":
                    draw.line([(x2, y2), bottom_right], fill="red", width=3)
                    draw.line([(x1, y2), bottom_left], fill="red", width=3)

            if zoom_direction_y == "bottom":
                if zoom_direction_x == "left":
                    draw.line([(x2, y1), top_right], fill="red", width=3)
                elif zoom_direction_x == "right":
                    draw.line([(x1, y1), top_left], fill="red", width=3)
                elif zoom_direction_x == "center":
                    draw.line([(x1, y1), top_left], fill="red", width=3)
                    draw.line([(x2, y1), top_right], fill="red", width=3)

            if zoom_direction_y == "center":
                if zoom_direction_x == "left":
                    draw.line([(x2, y2), bottom_right], fill="red", width=3)
                    draw.line([(x2, y1), top_right], fill="red", width=3)
                elif zoom_direction_x == "right":
                    draw.line([(x1, y2), bottom_left], fill="red", width=3)
                    draw.line([(x1, y1), top_left], fill="red", width=3)
                elif zoom_direction_x == "center":
                    draw.line([(x2, y2), bottom_right], fill="red", width=3)
                    draw.line([(x1, y2), bottom_left], fill="red", width=3)
                    draw.line([(x1, y1), top_left], fill="red", width=3)
                    draw.line([(x2, y1), top_right], fill="red", width=3)

        # crop padding on pan
        if scale == "pan":
            img = img.crop((thumb_x, thumb_y, thumb_x + slidethumb_width, thumb_y + slidethumb_height))

        return ImageTk.PhotoImage(img)

    def loadSlideshowAudioRow(self):
        canvas = self.frameAudio.getCanvas()

        frame = tk.Frame(canvas, padx=5, pady=5)

        self.buttonsAudio = []
        i = 0
        for i, audio in enumerate(self.sm.getBackgroundTracks()):
            # command=lambda c=i: self.onAudioClicked(c),
            b = ttk.Button(frame, text=os.path.basename(audio.file), style=SUNKABLE_BUTTON)
            b.grid(row=0, column=i, sticky=tk.NSEW)
            b.text = os.path.basename(audio.file)

            # see https://www.geeksforgeeks.org/python-tkinter-grid_location-and-grid_size-method/
            # see https://stackoverflow.com/a/37281388
            # see https://stackoverflow.com/a/37732268
            # see https://effbot.org/tkinterbook/tkinter-events-and-bindings.htm
            b.bind("<Button-1>", self.buttonDragStart)
            b.bind("<B1-Motion>", self.buttonDragMotion)
            b.bind("<ButtonRelease-1>", self.buttonDragStopAudio)

            self.buttonsAudio.append(b)

        # self.addAudioButton = ttk.Button(frame, text="Add audio", command=self.addAudio)
        # self.addAudioButton.grid(row=0, column=i + 1, sticky=tk.SW)

        self.addAudioButton["state"] = tk.NORMAL

        self.frameAudio.addFrame(frame)
        duration = self.sm.getAudioDuration() + self.sm.getVideoAudioDuration()
        self.audioDurationValue.set(self.formatDuration(duration))

    def buttonDragStart(self, event):
        widget = event.widget
        widget._drag_start_x = event.x
        widget._drag_start_y = event.y
        widget._col = widget.grid_info()['column']

    def buttonDragMotion(self, event):
        if self.moveSlidesBtn.get() > 0:
            widget = event.widget
            x = widget.winfo_x() - widget._drag_start_x + event.x
            y = widget.winfo_y() - widget._drag_start_y + event.y
            widget.place(x=x, y=y)
            widget.tkraise()

    def buttonDragStopAudio(self, event):
        widget = event.widget

        if self.moveSlidesBtn.get() > 0:
            x = widget.winfo_x() + event.x
            y = widget.winfo_y() + event.y
            (new_column, new_row) = self.frameAudio.getFrame().grid_location(x, y)

            # move button to new position
            # https://stackoverflow.com/a/3173159
            if widget._col != new_column:
                self.buttonsAudio.insert(new_column, self.buttonsAudio.pop(widget._col))
                self.sm.moveAudio(widget._col, new_column)

                # rearrange buttons in grid
                for i, btn in enumerate(self.buttonsAudio):
                    btn.grid(column=i)

        # Trigger Button Click
        # when using command the new button order is not respected
        # the button_id of the command is not changable
        button_id = widget.grid_info()['column']
        self.onAudioClicked(button_id)

    def buttonDragStopSlide(self, event):
        widget = event.widget

        if self.moveSlidesBtn.get() > 0:
            x = widget.winfo_x() + event.x
            y = widget.winfo_y() + event.y
            (new_column, new_row) = self.frameSlides.getFrame().grid_location(x, y)

            # move button to new position
            # https://stackoverflow.com/a/3173159
            if widget._col != new_column:
                self.buttons.insert(new_column, self.buttons.pop(widget._col))
                self.sm.moveSlide(widget._col, new_column)

                # rearrange buttons in grid
                for i, btn in enumerate(self.buttons):
                    btn.grid(column=i)

        # Trigger Button Click
        # when using command the new button order is not respected
        # the button_id of the command is not changable
        button_id = widget.grid_info()['column']
        self.onSlideClicked(button_id)

    def onAudioClicked(self, button_id):

        for btn in self.buttons:
            btn.state(['!pressed', '!disabled'])

        for btn in self.buttonsAudio:
            btn.state(['!pressed', '!disabled'])

        self.buttonsAudio[button_id].state(['pressed', 'disabled'])

        self.audio_selected = button_id
        audio = self.sm.getBackgroundTracks()[button_id]

        self.frameSlideSettings.clear()
        canvas3 = self.frameSlideSettings.getCanvas()

        optionsFrame = tk.Frame(canvas3, padx=5, pady=5)
        # optionsFrame.grid(sticky=tk.NSEW)
        optionsFrame.columnconfigure(0, weight=0)
        optionsFrame.columnconfigure(1, weight=1)

        generalframe = tk.LabelFrame(optionsFrame, text="General")
        generalframe.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)  # columnspan=2,

        fileLabel = tk.Label(generalframe, text="File")
        fileLabel.grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        fileEntry = tk.Entry(generalframe, width=70)
        fileEntry.insert(0, audio.file)
        fileEntry.configure(state='readonly')
        fileEntry.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)

        durationLabel = tk.Label(generalframe, text="Duration")
        durationLabel.grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
        durationEntry = tk.Entry(generalframe)
        durationEntry.insert(0, audio.duration)
        durationEntry.configure(state='readonly')
        durationEntry.grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)

        buttonsFrame = tk.Frame(optionsFrame)
        buttonsFrame.grid(row=3, columnspan=3, sticky=tk.NW, padx=4, pady=4)

        buttonDeleteAudio = tk.Button(buttonsFrame, text="Remove", command=(lambda: self.deleteAudio()))
        buttonDeleteAudio.pack()

        self.frameSlideSettings.addFrame(optionsFrame, tk.NW)

    def saveSlideshow(self):
        if self.sm:
            self.saveSlide()
            if not self.filename:
                self.saveAs()
            self.sm.saveConfig(self.filename)

    def saveAs(self):
        ftypes = [
            ('Slideshow config', '*.json')
        ]
        self.filename = asksaveasfilename(filetypes=ftypes, defaultextension=".json")
        if self.filename:
            self.title("%s (%s)" % (self.general_title, self.filename))
            self.saveSlideshow()

    def syncToAudio(self):
        logger.info("Sync slides durations to audio")
        self.saveSlide()
        self.sm.adjustDurationsFromAudio()
        self.resetGUI()
        self.loadSlideshowImagesRow()
        self.loadSlideshowAudioRow()
        self.videoDurationValue.set(self.formatDuration(self.sm.getTotalDuration()))

    def resetSlideDurations(self):
        logger.info("Reset slides durations to default")
        self.saveSlide()
        self.sm.resetSlideDurations()
        self.resetGUI()
        self.loadSlideshowImagesRow()
        self.loadSlideshowAudioRow()
        self.videoDurationValue.set(self.formatDuration(self.sm.getTotalDuration()))

    def createVideo(self):
        self.saveSlide()
        filename = asksaveasfilename()
        if filename:
            createVideoThread = threading.Thread(target=self.startVideoCreation, args=(filename,), daemon=True)
            createVideoThread.start()

    def startVideoCreation(self, output_file):
        burnSubtitles, srtInput, srtFilename, inputs, temp_filter_script = self.sm.prepareVideoProcessing(output_file)

        queue_length = self.sm.queue.getQueueLength()
        frames = self.sm.getFinalVideoFrames()

        progressPopup = ProgressFrame(self)
        progressPopup.create(self.slideshow_config["generate_temp"], queue_length, frames)

        for idx, item in enumerate(self.sm.queue.getQueue()):
            if progressPopup.is_cancelled:
                self.sm.cleanVideoProcessing()
                break
            print("Processing video %s/%s" % (idx + 1, queue_length))
            logger.info("Processing video %s/%s" % (idx + 1, queue_length))
            # logger.debug(item)
            tempFile = self.sm.queue.createTemporaryVideo(self.slideshow_config["ffmpeg"],
                                                          item,
                                                          self.slideshow_config["output_temp_parameters"],
                                                          self.slideshow_config["output_temp_codec"])

            if tempFile is None:
                print("Error while creating the temporary video file!")
                logger.error("Error while creating the temporary video file!")

            progressPopup.progress_var1.set(idx + 1)
            progressPopup.update()

        if not progressPopup.is_cancelled:
            cmd = self.sm.getFinalVideoCommand(
                output_file, burnSubtitles, srtInput, srtFilename, inputs, temp_filter_script, overwrite=True)

            cmd.append("-v")
            cmd.append("quiet")

            logger.info("FFMPEG started")
            logger.debug(" ".join(cmd))
            p = subprocess.Popen(" ".join(cmd), shell=True,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 universal_newlines=True)

            # set the process to the popup so when clicking cancel the command "q" can be send to ffmpeg
            progressPopup.setFinalVideoProcess(p)

            # read the stdout/stderr
            for line in iter(p.stdout.readline, ""):
                if p.returncode or progressPopup.is_cancelled:
                    break
                print(line.rstrip())
                m = re.search(r'^frame= *(\d+)', line)
                if m and m.group(1) is not None:
                    progress = m.group(1)
                    progressPopup.progress_var2.set(progress)
                    progressPopup.update()

            # wait till the process is finished (regular or cancelled)
            p.wait()
            logger.info("FFMPEG finished")

        self.sm.cleanVideoProcessing(temp_filter_script, srtFilename)

        # close popup
        progressPopup.destroy()

    def addSlide(self):
        self.saveSlide()
        filetypes = [".%s" % type for type in self.slideshow_config["IMAGE_EXTENSIONS"]
                     + self.slideshow_config["VIDEO_EXTENSIONS"]]

        ftypes = [
            ('Slide Files', " ".join(filetypes))
        ]

        filenames = askopenfilenames(filetypes=ftypes)
        for file in list(filenames):
            self.sm.addSlide(file, self.slide_selected)
        self.frameSlides.clear()
        self.frameSlideSettings.clear()
        self.loadSlideshowImagesRow()

    def deleteSlide(self):
        self.sm.removeSlide(self.slide_selected)
        self.frameSlides.clear()
        self.frameSlideSettings.clear()
        self.loadSlideshowImagesRow()

    def addAudio(self):
        self.saveSlide()
        filetypes = [".%s" % type for type in self.slideshow_config["AUDIO_EXTENSIONS"]]

        ftypes = [
            ('Audio Files', " ".join(filetypes))
        ]

        filenames = askopenfilenames(filetypes=ftypes)
        for file in list(filenames):
            self.sm.addAudio(file)
        self.frameAudio.clear()
        self.frameSlideSettings.clear()
        self.loadSlideshowAudioRow()

    def deleteAudio(self):
        self.sm.removeAudio(self.audio_selected)
        self.frameAudio.clear()
        self.frameSlideSettings.clear()
        self.loadSlideshowAudioRow()

    def formatDuration(self, seconds):
        s = int(seconds % 60)
        m = int((seconds / 60) % 60)
        h = int(seconds / (60 * 60)) % 24

        return '%02d:%02d:%02d' % (h, m, s)
