# https://stackoverflow.com/a/49681192
# https://stackoverflow.com/q/49873626


import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
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
import itertools

import logging

logger = logging.getLogger("kburns-slideshow")

import subprocess

import threading
import re

# https://stackoverflow.com/a/44633014
import sys
sys.path.append("..")
from slideshow.SlideManager import SlideManager
from slideshow.SlideManager import Slide, ImageSlide, VideoSlide

SUNKABLE_BUTTON = 'SunkableButton.TButton'

class App(tk.Tk):
    def __init__(self, title="", *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        self.general_title = title

        self.title(self.general_title)
        self.configure(background="Gray")
        
        # scale master frame to total Tk
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.geometry("800x800") #Width x Height

        master_frame = tk.Frame(self)
        master_frame.grid(sticky=tk.NSEW)
        
        # scale subframes to width of master frame
        master_frame.columnconfigure(0, weight=1)
        # top row(s) not changable
        master_frame.rowconfigure(0, weight=0)
        master_frame.rowconfigure(1, weight=0)
        # scale bottom row to height of master frame
        master_frame.rowconfigure(2, weight=1)

        # Image Frame with fill parent (sticky=tk.NSEW)
        self.frameSlides = ScrollFrame(master_frame, 100, False)
        self.frameSlides.grid(row=0, column=0, sticky=tk.NSEW)
        
        # Image Frame with fill parent (sticky=tk.NSEW)
        self.frameAudio = ScrollFrame(master_frame, 50, False)
        self.frameAudio.grid(row=1, column=0, sticky=tk.NSEW)        
        
        # Bottom Frame with fill parent (sticky=tk.NSEW)
        self.frameSlideSettings = ScrollFrame(master_frame, 100)
        self.frameSlideSettings.grid(row=2, column=0, sticky=tk.NSEW)
        
        # Buttons Frame
        frameActions = tk.Frame(master_frame, height=50)
        frameActions.grid(row=3, column=0, sticky=tk.NSEW, padx=5, pady=2)
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
        
        #buttonSave = tk.Button(frameActions, text="Save Configuration", command=self.saveSlideshow)
        #buttonSave.grid(row=0, column=2, rowspan = 2, sticky=tk.NW, padx=2)
        
        self.moveSlidesBtn = tk.IntVar()
        moveButton = ttk.Checkbutton(frameActions, text="Move slides/audio", variable=self.moveSlidesBtn)
        moveButton.grid(row=0, column=3, rowspan = 2, sticky=tk.W, padx=2)
        
        buttonSync = tk.Button(frameActions, text="Sync Video to Audio", command=self.syncToAudio)
        buttonSync.grid(row=0, column=4, rowspan = 2, sticky=tk.W, padx=2)
        
        buttonCreateVideo = tk.Button(frameActions, text="Create Video", command=self.createVideo)
        buttonCreateVideo.grid(row=0, column=5, rowspan = 2, sticky=tk.W, padx=2)
        
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
        self.transition_choices = [package_name for importer, package_name, _ in pkgutil.iter_modules([os.path.dirname(os.path.realpath(os.path.dirname(__file__)))+"/slideshow/transitions"])]
        self.transition_choices.append(" - None - ")
        zoom_direction_possibilities = [["top", "center", "bottom"], ["left", "center", "right"], ["in", "out"]]
        self.zoom_direction_choices = ["random", "none"] + list(map(lambda x: "-".join(x), itertools.product(*zoom_direction_possibilities)))
        self.scale_mode_choices = ["auto", "pad", "pan", "crop_center"]
        
        self.config_path = os.path.dirname(os.path.realpath(os.path.dirname(__file__)))+'/config.json'
        self.init() 
        # create empty slideshow
        # self.createSlideshow()
        
        # Save Slide Input Fields
        self.inputTransition = tk.StringVar()
        self.inputZoomDirection = tk.StringVar()
        self.inputScaleMode = tk.StringVar()
        
        self.inputforceNoAudio = tk.BooleanVar()
        self.inputvideoStart = tk.StringVar()
        self.inputvideoEnd = tk.StringVar()
        
        self.inputDuration = tk.StringVar()
        self.inputZoomRate = tk.StringVar()
        self.inputDurationMin = tk.StringVar()
        self.inputDurationTransition = tk.StringVar()
        
        self.inputSubtitle = tk.StringVar()
        self.inputOverlayTitle = tk.StringVar()
        self.inputOverlayFont = tk.StringVar()
        self.inputOverlayFontFile = tk.StringVar()
        self.inputOverlayFontSize = tk.StringVar()
        self.inputOverlayDuration = tk.StringVar()
        self.inputOverlayTransition = tk.StringVar()
        
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
        if self.hasSlides() and messagebox.askyesno("Restart", "To apply general slide settings to the current slideshow, the current slideshow needs to be reloaded. \n\nDo you want to reload the slides?"):
            self.createSlideshow(input_files, audio_files)
        
    def slideshowSettingsWindow(self):
        filewin = SettingsFrame(self)

        choices = {"zoom_direction": self.zoom_direction_choices, "transition": self.transition_choices, "scale_mode": self.scale_mode_choices}
        filewin.create(self.slideshow_config, choices)
        
        filewin.protocol("WM_DELETE_WINDOW", (lambda: self.onCloseSlideshowSettings(filewin)))
        
    def generalSettingsWindow(self):
        filewin = ConfigFrame(self)

        choices = {"zoom_direction": self.zoom_direction_choices, "transition": self.transition_choices, "scale_mode": self.scale_mode_choices}
        filewin.create(self.config_path, choices)
        
        #filewin.protocol("WM_DELETE_WINDOW", (lambda: self.onCloseTopLevel(filewin)))

        
    # see https://stackoverflow.com/a/39059073
    # see https://stackoverflow.com/a/51406895
    def checkEntryModification(self, event):
        self.slide_changed = True
        
        slide = self.sm.getSlides()[self.slide_selected]
        
        zd = self.inputZoomDirection.get() if isinstance(slide, ImageSlide) else None
        zr = self.inputZoomRate.get() if isinstance(slide, ImageSlide) else None
        sc = self.inputScaleMode.get() if isinstance(slide, ImageSlide) else None
        photo = self.getPreviewImage(self.buttons[self.slide_selected].image_path, zd, zr, sc)
        
        self.imageLabel.configure(image=photo)
        self.imageLabel.image = photo
        
    def saveSlide(self):
        if self.slide_changed:
            slide = self.sm.getSlides()[self.slide_selected]

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
                
                slide.setZoomDirection(self.inputZoomDirection.get())
                slide.setScaleMode(self.inputScaleMode.get())
            
            if isinstance(slide, VideoSlide):
                slide.setForceNoAudio(self.inputforceNoAudio.get())
                slide.start = float(self.inputvideoStart.get()) if float(self.inputvideoStart.get()) > 0 else None
                slide.end = float(self.inputvideoEnd.get()) if float(self.inputvideoEnd.get()) > 0 and float(self.inputvideoEnd.get()) < slide.getDuration() else None
                slide.calculateDurationAfterTrimming()
            
            slide.title = self.inputSubtitle.get() if len(self.inputSubtitle.get())>0 else None
            
            if len(self.inputOverlayTitle.get())>0 or len(self.inputOverlayFont.get())>0 or len(self.inputOverlayFontFile.get())>0 or len(self.inputOverlayFontSize.get())>0 or len(self.inputOverlayDuration.get())>0 or len(self.inputOverlayTransition.get())>0:
                overlay_text = {}
                if len(self.inputOverlayTitle.get())>0:
                    overlay_text["title"] = self.inputOverlayTitle.get()
                if len(self.inputOverlayFont.get())>0:
                    overlay_text["font"] = self.inputOverlayFont.get()
                if len(self.inputOverlayFontFile.get())>0:
                    overlay_text["font_file"] = self.inputOverlayFontFile.get()
                if len(self.inputOverlayFontSize.get())>0:
                    overlay_text["font_size"] = float(self.inputOverlayFontSize.get())
                if len(self.inputOverlayDuration.get())>0:
                    overlay_text["duration"] = float(self.inputOverlayDuration.get())
                if len(self.inputOverlayTransition.get())>0:
                    overlay_text["transition_x"] = self.inputOverlayTransition.get()
                    
                slide.overlay_text = overlay_text if overlay_text else None
            
            self.slide_changed = False
            
            # Recalculate video duration
            duration = self.sm.getTotalDuration()
            self.videoDurationValue.set(self.formatDuration(duration))
    
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
                self.title("%s (%s)" %(self.general_title, self.filename))
        except Exception as e:
            print("file must be a JSON file")
            print(e)
            logger.error("file %s must be a JSON file", self.filename)
    
    def createSlideshow(self, input_files = [], audio_files = []):
        self.frameSlides.clear()
        self.frameAudio.clear()
        self.frameSlideSettings.clear()
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
            messagebox.showerror("Error", "Could not initiate Slideshow Manager.\nPlease check general Settings.\n\nError: %s" %(e))
            return False
            
        return True
    
    def loadSlideshowImagesRow(self):
        canvas2 = self.frameSlides.getCanvas()
        
        images_frame = tk.Frame(canvas2, padx=5, pady=5)
        
        basewidth = 150
        
        self.buttons = []
        i = 0
        for i, slide in enumerate(self.sm.getSlides()):
            img_path = slide.file
            if isinstance(slide, VideoSlide):
                video_input_path = slide.file
                thumb_name = os.path.splitext(os.path.basename(video_input_path))[0]
                img_path = os.path.join('temp', 'thumbnail_%s.jpg' %(i))
                subprocess.call([self.slideshow_config["ffmpeg"], '-i', slide.file, '-ss', '00:00:00.000', '-vframes', '1', '-hide_banner', '-v', 'quiet', '-y', img_path])
                self.thumbnails.append(img_path)
        
            # https://stackoverflow.com/a/44978329
            img = Image.open(img_path)
            
            img.thumbnail((basewidth, basewidth/2))

            photo = ImageTk.PhotoImage(img)

            # https://stackoverflow.com/a/45733411
            # https://stackoverflow.com/questions/50787864/how-do-i-make-a-tkinter-button-in-an-list-of-buttons-return-its-index#comment88609106_50787933
            # command=lambda c=i: self.onSlideClicked(c), 
            b = ttk.Button(images_frame,image=photo, style=SUNKABLE_BUTTON)
            b.image = photo # keep a reference
            b.grid(row=0, column=i, sticky=tk.NSEW)
            
            # save reference to image path
            b.image_path = img_path
            
            b.bind("<Button-1>", self.buttonDragStart)
            b.bind("<B1-Motion>", self.buttonDragMotion)
            b.bind("<ButtonRelease-1>", self.buttonDragStopSlide)
            
            self.buttons.append(b)
        
        addButton = ttk.Button(images_frame, text="Add slide", command=self.addSlide)
        addButton.grid(row=0, column=i+1, sticky=tk.SW)
        
        self.frameSlides.addFrame(images_frame)
        duration = self.sm.getTotalDuration()
        self.videoDurationValue.set(self.formatDuration(duration))
        
    def onSlideClicked(self, button_id):
        for btn in self.buttons:
            btn.state(['!pressed', '!disabled'])
            
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
        #optionsFrame.grid(sticky=tk.NSEW)
        optionsFrame.columnconfigure(0, weight=0)
        optionsFrame.columnconfigure(1, weight=1)

        generalframe = tk.LabelFrame(optionsFrame, text="General")
        generalframe.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5) #columnspan=2, 
        
        buttonsFrame = tk.Frame(optionsFrame)
        buttonsFrame.grid(row=1, columnspan=3, sticky=tk.NW, padx=4, pady=4)
        
        #buttonSaveSlide = tk.Button(buttonsFrame, text="Save", command=(lambda: self.saveSlide()))
        #buttonSaveSlide.pack()
        buttonDeleteSlide = tk.Button(buttonsFrame, text="Delete", command=(lambda: self.deleteSlide()))
        buttonDeleteSlide.pack()
        
        fileLabel = tk.Label(generalframe, text="File")
        fileLabel.grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        fileEntry = tk.Entry(generalframe, width=70)
        fileEntry.insert(0, slide.file)
        fileEntry.configure(state='readonly')
        fileEntry.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)

        transitionframe = tk.LabelFrame(optionsFrame, text="Transition")
        transitionframe.grid(row=2, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        if not slide.transition is None:
            self.inputTransition.set(slide.transition)
        else:
            self.inputTransition.set(" - None - ")
        transitionLabel = tk.Label(transitionframe, text="Transition")
        transitionLabel.grid(row=0, column=0, sticky=tk.E, padx=4, pady=4)
        transitionCombo = ttk.Combobox(transitionframe, values=self.transition_choices, width=30, textvariable=self.inputTransition)
        transitionCombo.grid(row=0, column=1, sticky=tk.E, padx=4, pady=4)
        transitionCombo.bind("<<ComboboxSelected>>", self.checkEntryModification)
        
        self.inputDurationTransition.set(slide.fade_duration)
        durationFadeLabel = tk.Label(transitionframe, text="Duration")
        durationFadeLabel.grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
        durationFadeEntry = tk.Entry(transitionframe, validate='all', validatecommand=(vcmd, '%P'), textvariable=self.inputDurationTransition)
        durationFadeEntry.grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)
        durationFadeEntry.bind("<KeyRelease>",self.checkEntryModification)
        
        if isinstance(slide, ImageSlide):
            imageframe = tk.LabelFrame(optionsFrame, text="Image Options")
            imageframe.grid(row=3, column=0, sticky=tk.NSEW, padx=5, pady=5)
            
            self.inputDurationMin.set(slide.slide_duration_min)
            durationMinLabel = tk.Label(imageframe, text="Duration (min)")
            durationMinLabel.grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
            durationMinEntry = tk.Entry(imageframe, validate='all', validatecommand=(vcmd, '%P'), textvariable=self.inputDurationMin)
            durationMinEntry.grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)
            durationMinEntry.bind("<KeyRelease>", self.checkEntryModification)
            
            self.inputZoomDirection.set(slide.getZoomDirection())
            zoomDirectionLabel = tk.Label(imageframe, text="Zoom Direction")
            zoomDirectionLabel.grid(row=2, column=0, sticky=tk.W, padx=4, pady=4)
            zoomDirectionCombo = ttk.Combobox(imageframe, values=self.zoom_direction_choices, textvariable=self.inputZoomDirection)
            zoomDirectionCombo.grid(row=2, column=1, sticky=tk.E, padx=4, pady=4)
            zoomDirectionCombo.bind("<<ComboboxSelected>>", self.checkEntryModification)
            
            self.inputZoomRate.set(slide.zoom_rate)
            zoomRateLabel = tk.Label(imageframe, text="Zoom Rate")
            zoomRateLabel.grid(row=3, column=0, sticky=tk.W, padx=4, pady=4)
            zoomRateEntry = tk.Entry(imageframe, validate='all', validatecommand=(vcmd, '%P'), textvariable=self.inputZoomRate)
            zoomRateEntry.grid(row=3, column=1, sticky=tk.W, padx=4, pady=4)
            zoomRateEntry.bind("<KeyRelease>",self.checkEntryModification)
            
            self.inputScaleMode.set(slide.scale)
            scaleModeLabel = tk.Label(imageframe, text="Scale Mode")
            scaleModeLabel.grid(row=4, column=0, sticky=tk.W, padx=4, pady=4)
            scaleModeCombo = ttk.Combobox(imageframe, values=self.scale_mode_choices, textvariable=self.inputScaleMode)
            scaleModeCombo.grid(row=4, column=1, sticky=tk.W, padx=4, pady=4)
            scaleModeCombo.bind("<<ComboboxSelected>>", self.checkEntryModification)
        
        if isinstance(slide, VideoSlide):
            videoframe = tk.LabelFrame(optionsFrame, text="Video Options")
            videoframe.grid(row=3, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
            self.inputforceNoAudio.set(slide.force_no_audio)
            forceNoAudioLabel = tk.Label(videoframe, text="No Audio")
            forceNoAudioLabel.grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
            forceNoAudioCheckBox = tk.Checkbutton(videoframe, var=self.inputforceNoAudio)
            forceNoAudioCheckBox.grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)
            forceNoAudioCheckBox.bind("<ButtonRelease>",self.checkEntryModification)
            
            self.inputvideoStart.set(slide.start if slide.start is not None else -1)
            videoStartLabel = tk.Label(videoframe, text="Video Start")
            videoStartLabel.grid(row=2, column=0, sticky=tk.W, padx=4, pady=4)
            videoStartEntry = tk.Entry(videoframe, textvariable=self.inputvideoStart)
            videoStartEntry.grid(row=2, column=1, sticky=tk.W, padx=4, pady=4)
            videoStartEntry.bind("<KeyRelease>",self.checkEntryModification)
            
            self.inputvideoEnd.set(slide.end if slide.end is not None else -1)
            videoEndLabel = tk.Label(videoframe, text="Video End")
            videoEndLabel.grid(row=3, column=0, sticky=tk.W, padx=4, pady=4)
            videoEndEntry = tk.Entry(videoframe, textvariable=self.inputvideoEnd)
            videoEndEntry.grid(row=3, column=1, sticky=tk.W, padx=4, pady=4)
            videoEndEntry.bind("<KeyRelease>",self.checkEntryModification)
        
        if isinstance(slide, ImageSlide):
            durationFrame = imageframe
        else:
            durationFrame = videoframe
        self.inputDuration.set(slide.getDuration())
        durationLabel = tk.Label(durationFrame, text="Duration")
        durationLabel.grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        durationEntry = tk.Entry(durationFrame, validate='all', validatecommand=(vcmd, '%P'), textvariable=self.inputDuration)
        durationEntry.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)
        durationEntry.bind("<KeyRelease>",self.checkEntryModification)
        
        
        subtitleFrame = tk.LabelFrame(optionsFrame, text="Subtitle")
        subtitleFrame.grid(row=4, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        self.inputSubtitle.set(slide.title if slide.title else "")
        subtitleLabel = tk.Label(subtitleFrame, text="Subtitle")
        subtitleLabel.grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        subtitleEntry = tk.Entry(subtitleFrame, textvariable=self.inputSubtitle, width=50)
        subtitleEntry.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)
        subtitleEntry.bind("<KeyRelease>", self.checkEntryModification)
        
        overlayFrame = tk.LabelFrame(optionsFrame, text="Overlay")
        overlayFrame.grid(row=5, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        self.inputOverlayTitle.set(slide.overlay_text["title"] if slide.overlay_text and "title" in slide.overlay_text else "")
        overlayTitleLabel = tk.Label(overlayFrame, text="Title")
        overlayTitleLabel.grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        overlayTitleEntry = tk.Entry(overlayFrame, textvariable=self.inputOverlayTitle, width=50)
        overlayTitleEntry.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)
        overlayTitleEntry.bind("<KeyRelease>", self.checkEntryModification)
        
        self.inputOverlayFont.set(slide.overlay_text["font"] if slide.overlay_text and "font" in slide.overlay_text else "")
        overlayFontLabel = tk.Label(overlayFrame, text="Font")
        overlayFontLabel.grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
        overlayFontEntry = tk.Entry(overlayFrame, textvariable=self.inputOverlayFont, width=50)
        overlayFontEntry.grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)
        overlayFontEntry.bind("<KeyRelease>", self.checkEntryModification)
        
        self.inputOverlayFontFile.set(slide.overlay_text["font_file"] if slide.overlay_text and "font_file" in slide.overlay_text else "")
        overlayFontFileLabel = tk.Label(overlayFrame, text="Font file")
        overlayFontFileLabel.grid(row=2, column=0, sticky=tk.W, padx=4, pady=4)
        overlayFontFileEntry = tk.Entry(overlayFrame, textvariable=self.inputOverlayFontFile, width=50)
        overlayFontFileEntry.grid(row=2, column=1, sticky=tk.W, padx=4, pady=4)
        overlayFontFileEntry.bind("<KeyRelease>", self.checkEntryModification)
        
        self.inputOverlayFontSize.set(slide.overlay_text["font_size"] if slide.overlay_text and "font_size" in slide.overlay_text else "")
        overlayFontSizeLabel = tk.Label(overlayFrame, text="Font size")
        overlayFontSizeLabel.grid(row=3, column=0, sticky=tk.W, padx=4, pady=4)
        overlayFontSizeEntry = tk.Entry(overlayFrame, validate='all', validatecommand=(vcmd, '%P'), textvariable=self.inputOverlayFontSize)
        overlayFontSizeEntry.grid(row=3, column=1, sticky=tk.W, padx=4, pady=4)
        overlayFontSizeEntry.bind("<KeyRelease>", self.checkEntryModification)
        
        self.inputOverlayDuration.set(slide.overlay_text["duration"] if slide.overlay_text and "duration" in slide.overlay_text else "")
        overlayFontDurationLabel = tk.Label(overlayFrame, text="Duration")
        overlayFontDurationLabel.grid(row=4, column=0, sticky=tk.W, padx=4, pady=4)
        overlayFontDurationEntry = tk.Entry(overlayFrame, validate='all', validatecommand=(vcmd, '%P'), textvariable=self.inputOverlayDuration)
        overlayFontDurationEntry.grid(row=4, column=1, sticky=tk.W, padx=4, pady=4)
        overlayFontDurationEntry.bind("<KeyRelease>", self.checkEntryModification)
        
        self.inputOverlayTransition.set(slide.overlay_text["transition_x"] if slide.overlay_text and "transition_x" in slide.overlay_text else "")
        overlayTransitionLabel = tk.Label(overlayFrame, text="Transition Direction")
        overlayTransitionLabel.grid(row=5, column=0, sticky=tk.W, padx=4, pady=4)
        overlayTransitionCombo = ttk.Combobox(overlayFrame, values=["center", "right-in", "left-in"], textvariable=self.inputOverlayTransition)
        overlayTransitionCombo.grid(row=5, column=1, sticky=tk.W, padx=4, pady=4)
        overlayTransitionCombo.bind("<<ComboboxSelected>>", self.checkEntryModification)
        
        # Right column (image preview)
        imageframe = tk.LabelFrame(optionsFrame, text="Image")
        imageframe.grid(row=0, column=1, rowspan = 5, sticky=tk.NW, padx=5, pady=5)
        
        # get image path from button and create "bigger" preview
        zd = slide.getZoomDirection() if isinstance(slide, ImageSlide) else None
        zr = slide.zoom_rate if isinstance(slide, ImageSlide) else None
        sc = slide.scale if isinstance(slide, ImageSlide) else None
        photo = self.getPreviewImage(self.buttons[button_id].image_path, zd, zr, sc)
        
        self.imageLabel = tk.Label(imageframe, image=photo)
        self.imageLabel.grid(row=0, column=0, sticky=tk.E, padx=4, pady=4)
        # keep a reference
        self.imageLabel.image = photo        
        
        
        self.frameSlideSettings.addFrame(optionsFrame, tk.NW)
    
    def getPreviewImage(self, img_path, zoom_direction = None, zoom_rate = None, scale = None):
        output_ratio = float(self.slideshow_config["output_width"])/float(self.slideshow_config["output_height"])
        thumb_width = 250
        thumb_height = int(thumb_width/output_ratio)
        
        slideImage = Image.open(img_path)
        slideImage_width, slideImage_height = slideImage.size
        slideImage_ratio = slideImage_width/slideImage_height
        
        slidethumb_width, slidethumb_height = [thumb_width, thumb_height]
        if scale == "crop_center":
            slidethumb_width, slidethumb_height = [thumb_width, int(thumb_width/slideImage_ratio)] if slideImage_ratio < output_ratio else [int(thumb_height*slideImage_ratio), thumb_height]
        elif scale == "pad" or scale == "pan":
            slidethumb_width, slidethumb_height = [thumb_width, int(thumb_width/slideImage_ratio)] if slideImage_ratio > output_ratio else [int(thumb_height*slideImage_ratio), thumb_height]
            
        slideImage.thumbnail((slidethumb_width, slidethumb_height))
            
        img = Image.new('RGB', (thumb_width, thumb_height), color = 'black')
        thumb_x = int((thumb_width - slidethumb_width) / 2)
        thumb_y = int((thumb_height - slidethumb_height) / 2)
        img.paste(slideImage, (thumb_x, thumb_y))
        
        # transition preview
        if zoom_direction is not None and zoom_rate is not None:
            zd = zoom_direction.split("-")
            if len(zd) > 1: 
                direction_x = zoom_direction.split("-")[1]
                direction_y = zoom_direction.split("-")[0]
            
                draw = ImageDraw.Draw(img)
                width, height = img.size# [thumb_width, int(thumb_width/output_ratio)]
                output_width = width
                output_height = int(output_width/output_ratio)
                x1 = 0
                y1 = 0
                x2 = 0
                y2 = 0
                
                z_initial = 1
                z_step = float(zoom_rate)
                if scale == "pan":
                    z_initial = slideImage_ratio/output_ratio if slideImage_ratio > output_ratio else output_ratio/slideImage_ratio
                    z_step = z_step*z_initial
                
                scale_factor = 1/(z_initial+z_step)
                
                if direction_x == "left":
                    x1 = 0
                elif direction_x == "right":
                    x1 = width - width*scale_factor
                elif direction_x == "center":
                    x1 = (width - output_width*scale_factor)/2
                    
                if direction_y == "top":
                    y1 = 0
                elif direction_y == "bottom":
                    y1 = height - output_height*scale_factor
                elif direction_y == "center":
                    y1 = (height - output_height*scale_factor)/2
                
                x2 = x1 + output_width*scale_factor
                y2 = y1 + output_height*scale_factor
                
                # adjust coordinates for panning
                if scale == "pan":
                    if direction_x == "left":
                        x1 = x1 + thumb_x
                        x2 = x2 + thumb_x
                    elif direction_x == "right":
                        x1 = x1 - thumb_x
                        x2 = x2 - thumb_x
                        
                    if direction_y == "top":
                        y1 = y1 + thumb_y
                        y2 = y2 + thumb_y
                    elif direction_y == "bottom":
                        y1 = y1 - thumb_y
                        y2 = y2 - thumb_y
                draw.rectangle([(x1, y1), (x2, y2)], outline ="red", width=3)
                
                # draw initial rectangle on panning
                if scale == "pan":
                    # horizontal image in landscape output
                    if slideImage_ratio < output_ratio:
                        img_w = slidethumb_width
                        img_h = slidethumb_width/output_ratio
                        
                        if direction_y == "top":
                            x0_1 = thumb_x
                            y0_1 = height - thumb_y
                            x0_2 = thumb_x + img_w
                            y0_2 = height - thumb_y - img_h
                        elif direction_y == "bottom":
                            x0_1 = thumb_x
                            y0_1 = thumb_y
                            x0_2 = thumb_x + img_w
                            y0_2 = thumb_y + img_h
                        elif direction_y == "center":
                            x0_1 = thumb_x
                            y0_1 = (height - thumb_y - img_h)/2
                            x0_2 = thumb_x + img_w
                            y0_2 = y0_1 + img_h
                    else:
                        img_w = slidethumb_height*output_ratio
                        img_h = slidethumb_height
                        
                        if direction_x == "left":
                            x0_1 = width - thumb_x - img_w
                            y0_1 = height - thumb_y
                            x0_2 = width - thumb_x
                            y0_2 = height - thumb_y - img_h
                        elif direction_x == "right":
                            x0_1 = thumb_x
                            y0_1 = height - thumb_y
                            x0_2 = thumb_x + img_w
                            y0_2 = height - thumb_y - img_h
                        elif direction_x == "center":
                            x0_1 = (width - thumb_x - img_w)/2
                            y0_1 = thumb_y
                            x0_2 = x0_1 + img_w
                            y0_2 = thumb_y + img_h
                    draw.rectangle([(x0_1, y0_1), (x0_2, y0_2)], outline ="red", width=3)
                
                # direction
                if scale == "pad" or scale == "crop_center":
                    top_left = (0,0)
                    top_right = (width, 0)
                    bottom_left = (0, height)
                    bottom_right = (width, height)
                elif scale == "pan":
                    top_left = (thumb_x,thumb_y)
                    top_right = (width-thumb_x, thumb_y)
                    bottom_left = (thumb_x, height-thumb_y)
                    bottom_right = (width-thumb_x, height-thumb_y)
                    
                    if (direction_y == "center" and slideImage_ratio < output_ratio) or (direction_x == "center" and not slideImage_ratio < output_ratio):
                        top_left = (x0_1, y0_1)
                        top_right = (x0_2, y0_1)
                        bottom_left = (x0_1, y0_2)
                        bottom_right = (x0_2, y0_2)
                    
                if direction_y == "top":
                    if direction_x == "left":
                        draw.line([(x2, y2), bottom_right], fill ="red", width=3)
                    elif direction_x == "right":
                        draw.line([(x1, y2), bottom_left], fill ="red", width=3)
                    elif direction_x == "center":
                        draw.line([(x2, y2), bottom_right], fill ="red", width=3)
                        draw.line([(x1, y2), bottom_left], fill ="red", width=3)
                        
                if direction_y == "bottom":
                    if direction_x == "left":
                        draw.line([(x2, y1), top_right], fill ="red", width=3)
                    elif direction_x == "right":
                        draw.line([(x1, y1), top_left], fill ="red", width=3)
                    elif direction_x == "center":
                        draw.line([(x1, y1), top_left], fill ="red", width=3)
                        draw.line([(x2, y1), top_right], fill ="red", width=3)
                        
                if direction_y == "center":
                    if direction_x == "left":
                        draw.line([(x2, y2), bottom_right], fill ="red", width=3)
                        draw.line([(x2, y1), top_right], fill ="red", width=3)
                    elif direction_x == "right":
                        draw.line([(x1, y2), bottom_left], fill ="red", width=3)
                        draw.line([(x1, y1), top_left], fill ="red", width=3)
                    elif direction_x == "center":
                        draw.line([(x2, y2), bottom_right], fill ="red", width=3)
                        draw.line([(x1, y2), bottom_left], fill ="red", width=3)
                        draw.line([(x1, y1), top_left], fill ="red", width=3)
                        draw.line([(x2, y1), top_right], fill ="red", width=3)
        
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
            #command=lambda c=i: self.onAudioClicked(c), 
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
        
        self.addAudioButton = ttk.Button(frame, text="Add audio", command=self.addAudio)
        self.addAudioButton.grid(row=0, column=i+1, sticky=tk.SW)
        
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
        #optionsFrame.grid(sticky=tk.NSEW)
        optionsFrame.columnconfigure(0, weight=0)
        optionsFrame.columnconfigure(1, weight=1)

        generalframe = tk.LabelFrame(optionsFrame, text="General")
        generalframe.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5) #columnspan=2, 
        
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

        buttonDeleteSlide = tk.Button(buttonsFrame, text="Delete", command=(lambda: self.deleteAudio()))
        buttonDeleteSlide.pack()        
        
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
            self.title("%s (%s)" %(self.general_title, self.filename))
            self.saveSlideshow()
    
    def syncToAudio(self):
        logger.info("Sync slides durations to audio")
        self.saveSlide()
        self.sm.adjustDurationsFromAudio()
        self.frameSlides.clear()
        self.frameAudio.clear()
        self.frameSlideSettings.clear()
        self.loadSlideshowImagesRow()
        self.loadSlideshowAudioRow()
        self.videoDurationValue.set(self.formatDuration(self.sm.getTotalDuration()))
        
    def createVideo(self):
        self.saveSlide()
        filename = asksaveasfilename()
        createVideoThread = threading.Thread(target=self.startVideoCreation, args=(filename,), daemon = True)
        createVideoThread.start()
        
    def startVideoCreation(self, output_file):
        burnSubtitles, srtInput, srtFilename, inputs, temp_filter_script = self.sm.prepareVideoProcessing(output_file)
        
        queue_length = self.sm.queue.getQueueLength()
        frames = self.sm.getFinalVideoFrames()
        
        progressPopup = ProgressFrame(self)
        progressPopup.create(self.slideshow_config["generate_temp"], queue_length, frames)
        
        for idx, item in enumerate(self.sm.queue.getQueue()):
            if progressPopup.is_cancelled:
                break
            print("Processing video %s/%s" %(idx+1, queue_length))
            logger.info("Processing video %s/%s" %(idx+1, queue_length))
            self.sm.queue.createTemporaryVideo(self.slideshow_config["ffmpeg"], item)
            progressPopup.progress_var1.set(idx+1)
            progressPopup.update()
        
        if not progressPopup.is_cancelled:
            cmd = self.sm.getFinalVideoCommand(output_file, burnSubtitles, srtInput, srtFilename, inputs, temp_filter_script, overwrite = True)
            
            cmd.append("-v")
            cmd.append("quiet")
            
            logger.info("FFMPEG started")
            logger.debug(" ".join(cmd))
            p = subprocess.Popen(" ".join(cmd), shell=True, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, universal_newlines = True)
            
            # set the process to the popup so when clicking cancel the command "q" can be send to ffmpeg
            progressPopup.setFinalVideoProcess(p)
            
            # read the stdout/stderr
            for line in iter(p.stdout.readline, ""):
                if p.returncode or progressPopup.is_cancelled:
                    break
                print(line.rstrip())
                m = re.search('^frame= *(\d+)', line)
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
        filetypes = [ ".%s" % type for type in self.slideshow_config["IMAGE_EXTENSIONS"] + self.slideshow_config["VIDEO_EXTENSIONS"]]    
    
        ftypes = [
            ('Slide Files', " ".join(filetypes))
        ]
            
        filenames = askopenfilenames(filetypes=ftypes)
        for file in list(filenames):
            self.sm.addSlide(file)
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
        filetypes = [ ".%s" % type for type in self.slideshow_config["AUDIO_EXTENSIONS"]]    
        
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
        s = int(seconds%60)
        m = int((seconds/60)%60)
        h = int(seconds/(60*60))%24
        
        return '%02d:%02d:%02d' % (h, m, s)