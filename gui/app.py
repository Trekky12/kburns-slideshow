# https://stackoverflow.com/a/49681192
# https://stackoverflow.com/q/49873626


import tkinter as tk
from PIL import Image, ImageTk
from tkinter.filedialog import askopenfilename, askopenfilenames, asksaveasfilename
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
        
        self.general_title = title

        self.title(self.general_title)
        self.configure(background="Gray")
        
        # scale master frame to total Tk
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.geometry("800x600") #Width x Height

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
        frameActions.grid(row=3, column=0, sticky=tk.NW, padx=5, pady=5)
        button_save = tk.Button(frameActions, text="Save Configuration", command=self.saveSlideshow)
        button_save.pack()
        
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
        
    def hasSlides(self):
        return self.sm and len(self.sm.getSlides()) > 0
        
    def on_closing(self):
        if self.hasSlides() and messagebox.askyesno("Quit", "Do you want to quit?"):
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
        if self.hasSlides() and messagebox.askyesno("Restart", "To apply general slide settings to the current slideshow, the current slideshow needs to be reloaded. \n\nDo you want to reload the slides?"):
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
            
            if self.inputTransition.get() != " - None - ":
                slide.transition = self.inputTransition.get()
            else:
                slide.transition = None
            
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
        self.title("%s (%s)" %(self.general_title, self.filename))
        try:
            with open(self.filename) as f:
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
            logger.error("file %s must be a JSON file", self.filename)
    
    def createSlideshow(self):
        self.frameSlides.clear()
        self.frameAudio.clear()
        self.frameSlideSettings.clear()
        self.generalmenu.entryconfig("Slideshow Settings", state="disabled")
        self.sm = SlideManager(self.slideshow_config, self.input_files, self.audio_files)
        self.loadSlideshowImagesRow()
        self.loadSlideshowAudioRow()
        self.generalmenu.entryconfig("Slideshow Settings", state="normal")
        self.filemenu.entryconfig("Save", state="normal")
        self.filemenu.entryconfig("Save As..", state="normal")
    
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
                img_path = 'temp\\thumbnail_%s.jpg' %(i)
                subprocess.call([self.slideshow_config["ffmpeg"], '-i', slide.file, '-ss', '00:00:00.000', '-vframes', '1', '-hide_banner', '-v', 'quiet', '-y', img_path])
                self.thumbnails.append(img_path)
        
            # https://stackoverflow.com/a/44978329
            img = Image.open(img_path)
            
            img.thumbnail((basewidth, basewidth/2))

            photo = ImageTk.PhotoImage(img)

            # https://stackoverflow.com/a/45733411
            # https://stackoverflow.com/questions/50787864/how-do-i-make-a-tkinter-button-in-an-list-of-buttons-return-its-index#comment88609106_50787933
            b = ttk.Button(images_frame,image=photo, command=lambda c=i: self.onSlideClicked(c), style=SUNKABLE_BUTTON)
            b.image = photo # keep a reference
            b.grid(row=0, column=i, sticky=tk.NSEW)
            
            self.buttons.append(b)
        
        addButton = ttk.Button(images_frame, text="Add slide", command=self.addSlide)
        addButton.grid(row=0, column=i+1, sticky=tk.SW)
        
        self.frameSlides.addFrame(images_frame)
        
    def onSlideClicked(self, button_id):
        for btn in self.buttons:
            btn.state(['!pressed', '!disabled'])
            
        for btn in self.buttonsAudio:
            btn.state(['!pressed', '!disabled'])
        
        self.buttons[button_id].state(['pressed'])
    
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
        
        
        buttonsFrame = tk.Frame(optionsFrame)
        buttonsFrame.grid(row=3, columnspan=3, sticky=tk.NW, padx=4, pady=4)
        
        #buttonSaveSlide = tk.Button(buttonsFrame, text="Save", command=(lambda: self.saveSlide()))
        #buttonSaveSlide.pack()
        buttonDeleteSlide = tk.Button(buttonsFrame, text="Delete", command=(lambda: self.deleteSlide()))
        buttonDeleteSlide.pack()
        
        
        self.frameSlideSettings.addFrame(optionsFrame, tk.NW)
        
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
            b.bind("<ButtonRelease-1>", self.buttonDragStop)
            
            self.buttonsAudio.append(b)
        
        self.addAudioButton = ttk.Button(frame, text="Add audio", command=self.addAudio)
        self.addAudioButton.grid(row=0, column=i+1, sticky=tk.SW)
        
        self.frameAudio.addFrame(frame)
        
    def buttonDragStart(self, event):
        widget = event.widget
        widget._drag_start_x = event.x
        widget._drag_start_y = event.y
        widget._col = widget.grid_info()['column']

    def buttonDragMotion(self, event):
        widget = event.widget
        x = widget.winfo_x() - widget._drag_start_x + event.x
        y = widget.winfo_y() - widget._drag_start_y + event.y
        widget.place(x=x, y=y)
        widget.tkraise()
            
    def buttonDragStop(self, event):
        widget = event.widget
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
    
    def onAudioClicked(self, button_id):     
        
        for btn in self.buttons:
            btn.state(['!pressed', '!disabled'])
    
        for btn in self.buttonsAudio:
            btn.state(['!pressed', '!disabled'])
        
        self.buttonsAudio[button_id].state(['pressed'])
        
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
        
    def addSlide(self):
    
        filetypes = self.slideshow_config["IMAGE_EXTENSIONS"] + self.slideshow_config["VIDEO_EXTENSIONS"]
    
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
        ftypes = [
            ('Audio Files', " ".join(self.slideshow_config["AUDIO_EXTENSIONS"]))
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