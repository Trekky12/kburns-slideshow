# https://stackoverflow.com/a/49681192
# https://stackoverflow.com/q/49873626


import tkinter as tk
from PIL import Image, ImageTk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import messagebox
from tkinter import ttk

from .ScrollFrame import ScrollFrame
from .SettingsFrame import SettingsFrame
from .ConfigFrame import ConfigFrame

import os
import json

import pkgutil
import itertools

import logging

logger = logging.getLogger("kburns-slideshow-gui")

import subprocess

# https://stackoverflow.com/a/44633014
import sys
sys.path.append("..")
from slideshow.SlideManager import SlideManager
from slideshow.SlideManager import Slide, ImageSlide, VideoSlide

SUNKABLE_BUTTON = 'SunkableButton.TButton'

class App(tk.Tk):
    def __init__(self, title="", *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title(title)
        self.configure(background="Gray")
        
        # scale master frame to total Tk
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.geometry("800x500") #Width x Height

        master_frame = tk.Frame(self)
        master_frame.grid(sticky=tk.NSEW)
        
        # scale subframes to width of master frame
        master_frame.columnconfigure(0, weight=1)
        # top row not changable
        master_frame.rowconfigure(0, weight=0)
        # scale bottom row to height of master frame
        master_frame.rowconfigure(1, weight=1)

        # Image Frame with fill parent (sticky=tk.NSEW)
        self.frame2 = ScrollFrame(master_frame, 100)
        self.frame2.grid(row=0, column=0, sticky=tk.NSEW)
        
        # Bottom Frame with fill parent (sticky=tk.NSEW)
        self.frame3 = ScrollFrame(master_frame, 100)
        self.frame3.grid(row=1, column=0, sticky=tk.NSEW)
        
        # Buttons Frame
        frame4 = tk.Frame(master_frame, height=50)
        button_save = tk.Button(frame4, text="Save Configuration", command=self.saveConfiguration)
        button_save.pack()
        frame4.grid(row=2, column=0, sticky=tk.NW)
        
        # Menu
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.openFile)
        filemenu.add_command(label="Save", command=self.saveConfiguration)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        
        self.generalmenu = tk.Menu(menubar, tearoff=0)
        self.generalmenu.add_command(label="Slideshow Settings", command=self.slideshowSettingsWindow, state="disabled")
        self.generalmenu.add_separator()
        self.generalmenu.add_command(label="General Settings", command=self.generalSettingsWindow)
        menubar.add_cascade(label="Settings", menu=self.generalmenu)
        
        self.config(menu=menubar)
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.buttons = []
        # https://stackoverflow.com/a/23355222
        # https://kite.com/python/docs/ttk.Style
        self.style = ttk.Style()
        self.style.configure(SUNKABLE_BUTTON, padding=2) 
        self.style.map(SUNKABLE_BUTTON, background=[('pressed', 'red'), ('disabled', 'red')])
        
        
        self.config_path = os.path.dirname(os.path.realpath(os.path.dirname(__file__)))+'/config.json'
        self.slideshow_config = {}
        with open(self.config_path) as config_file:
            self.slideshow_config = json.load(config_file)   
        
        self.thumbnails = []
        self.transition_choices = [package_name for importer, package_name, _ in pkgutil.iter_modules([os.path.dirname(os.path.realpath(os.path.dirname(__file__)))+"/slideshow/transitions"])]
        self.transition_choices.append(" - None - ")
        zoom_direction_possibilities = [["top", "center", "bottom"], ["left", "center", "right"], ["in", "out"]]
        self.zoom_direction_choices = ["random", "none"] + list(map(lambda x: "-".join(x), itertools.product(*zoom_direction_possibilities)))
        self.scale_mode_choices = ["auto", "pad", "pan", "crop_center"]
        
        self.filename = None
        self.input_files = []
        self.audio_files = []
        # Save selected slide index
        self.slide_selected = None
        
        self.slide_changed = False
        
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
        
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            # Delete thumbnails
            for file in self.thumbnails:
                if os.path.exists(file):
                    os.remove(file)
                    logger.debug("Delete %s", file)
            # Close 
            self.destroy()
            
    def onCloseSlideshowSettings(self, toplevel):
        # get new config
        self.slideshow_config.update(toplevel.getConfig())
        # close
        toplevel.destroy()
        # ask for reload
        if messagebox.askyesno("Restart", "To apply general slide settings to the current slideshow, the current slideshow needs to be reloaded. \n\nDo you want to reload the slides?"):
            self.createSlideshow()
        
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
        
    def saveSlide(self):
        if self.slide_changed:
            slide = self.sm.getSlides()[self.slide_selected]

            slide.setDuration(float(self.inputDuration.get()))
            slide.fade_duration = float(self.inputDurationTransition.get())
            slide.transition = self.inputTransition.get()
            
            if isinstance(slide, ImageSlide):
                slide.zoom_rate = float(self.inputZoomRate.get())
                slide.slide_duration_min = float(self.inputDurationMin.get())
                if slide.slide_duration_min > slide.getDuration():
                    slide.setDuration(slide.slide_duration_min)
                    self.durationEntry.delete(0, 'end')
                    self.durationEntry.insert(0, slide.getDuration())
                
                slide.setZoomDirection(self.inputZoomDirection.get())
                slide.setScaleMode(self.inputScaleMode.get())
            
            if isinstance(slide, VideoSlide):
                slide.setForceNoAudio(self.inputforceNoAudio.get())
                slide.start = float(self.inputvideoStart.get()) if float(self.inputvideoStart.get()) > 0 else None
                slide.end = float(self.inputvideoEnd.get()) if float(self.inputvideoEnd.get()) > 0 and float(self.inputvideoEnd.get()) < slide.getDuration() else None
                slide.calculateDurationAfterTrimming()
            
            self.slide_changed = False
    
    # see https://stackoverflow.com/a/46670374
    def validateDigit(self, P):
        if not P:
            return True
        try:
            float(P)
            return True
        except ValueError:
            return False
    
    def onButtonClicked(self, button_id):
        for btn in self.buttons:
            btn.state(['!pressed', '!disabled'])
        
        self.buttons[button_id].state(['pressed'])
    
        self.saveSlide()

        self.slide_selected = button_id        
        slide = self.sm.getSlides()[button_id]
        
        vcmd = (self.register(self.validateDigit))

        self.frame3.clear()
        canvas3 = self.frame3.getCanvas()
        
        optionsFrame = tk.Frame(canvas3, padx=5, pady=5)
        #optionsFrame.grid(sticky=tk.NSEW)
        optionsFrame.columnconfigure(0, weight=0)
        optionsFrame.columnconfigure(1, weight=1)

        generalframe = tk.LabelFrame(optionsFrame, text="General")
        generalframe.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5) #columnspan=2, 
        
        fileLabel = tk.Label(generalframe, text="File")
        fileLabel.grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        fileEntry = tk.Entry(generalframe, width=70)
        fileEntry.insert(0, slide.file)
        fileEntry.configure(state='readonly')
        fileEntry.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)

        transitionframe = tk.LabelFrame(optionsFrame, text="Transition")
        transitionframe.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
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
            imageframe.grid(row=2, column=0, sticky=tk.NSEW, padx=5, pady=5)
            
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
            videoframe.grid(row=2, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
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
        
        imageframe = tk.LabelFrame(optionsFrame, text="Image")
        imageframe.grid(row=0, column=1, rowspan = 3, sticky=tk.NW, padx=5, pady=5)
        
        imageLabel = tk.Label(imageframe, image=self.buttons[button_id].image)
        imageLabel.grid(row=0, column=0, sticky=tk.E, padx=4, pady=4)
        
        '''
        buttonsFrame = tk.Frame(optionsFrame)
        buttonsFrame.grid(row=1, columnspan=3, sticky=tk.NW, padx=4, pady=4)
        
        buttonSaveSlide = tk.Button(buttonsFrame, text="Save", command=(lambda: self.saveSlide()))
        buttonSaveSlide.pack()
        '''
        
        self.frame3.addFrame(optionsFrame, tk.NW)
        
        
        
    def openFile(self):
        ftypes = [
            ('Slideshow config', '*.json')
        ]
        self.filename = askopenfilename(filetypes=ftypes)
        self.loadSlideshow(self.filename)
    
    def loadSlideshow(self, filename):
        try:
            with open(filename) as f:
                file_content = json.load(f)    

                if "config" in file_content:
                    self.slideshow_config.update(file_content["config"])
                    logger.debug("overwrite config")
                
                if "slides" in file_content:
                    self.input_files = file_content["slides"]
                    logger.debug("get slides")
                
                if "audio" in file_content:
                    self.audio_files = file_content["audio"]
                    logger.debug("get audio")
            
            self.createSlideshow()
        except Exception as e:
            print("file must be a JSON file")
            print(e)
            logger.error("file %s must be a JSON file", filename)
    
    def createSlideshow(self):
        self.frame2.clear()
        self.frame3.clear()
        self.generalmenu.entryconfig("Slideshow Settings", state="disabled")
        self.sm = SlideManager(self.slideshow_config, self.input_files, self.audio_files)
        self.loadSlideshowImagesRow()
        self.generalmenu.entryconfig("Slideshow Settings", state="normal")
    
    def loadSlideshowImagesRow(self):
        canvas2 = self.frame2.getCanvas()
        
        images_frame = tk.Frame(canvas2, padx=5, pady=5)
        
        basewidth = 150
        
        self.buttons = []
        
        for i, slide in enumerate(self.sm.getSlides()):
            img_path = slide.file
            if isinstance(slide, VideoSlide):
                video_input_path = slide.file
                thumb_name = os.path.splitext(os.path.basename(video_input_path))[0]
                img_path = 'temp\\thumbnail_%s.jpg' %(i)
                subprocess.call([self.slideshow_config["ffmpeg"], '-i', slide.file, '-ss', '00:00:00.000', '-vframes', '1', '-hide_banner', '-v', 'quiet', '-y', img_path])
                self.thumbnails.append(img_path)
        
            # https://stackoverflow.com/a/44978329
            img = Image.open(img_path)
            
            img.thumbnail((basewidth, basewidth/2))

            photo = ImageTk.PhotoImage(img)

            # https://stackoverflow.com/a/45733411
            # https://stackoverflow.com/questions/50787864/how-do-i-make-a-tkinter-button-in-an-list-of-buttons-return-its-index#comment88609106_50787933
            b = ttk.Button(images_frame,image=photo, command=lambda c=i: self.onButtonClicked(c), style=SUNKABLE_BUTTON)
            b.image = photo # keep a reference
            b.grid(row=0, column=i, sticky=tk.NSEW)
            
            self.buttons.append(b)
        
        addButton = ttk.Button(images_frame, text="Add slide", command=self.addSlide)
        addButton.grid(row=0, column=i+1, sticky=tk.SW)
        
        self.frame2.addFrame(images_frame)
        
    def saveConfiguration(self):
        if self.sm:
            ftypes = [
                ('Slideshow config', '*.json')
            ]
            filename = asksaveasfilename(filetypes=ftypes, defaultextension=".json")
            self.saveSlide()
            self.sm.saveConfig(filename)
        
    def addSlide(self):
        filename = askopenfilename()
        self.sm.addSlide(filename)
        self.loadSlideshowImagesRow()