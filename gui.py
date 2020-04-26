# https://stackoverflow.com/a/49681192
# https://stackoverflow.com/q/49873626

# https://stackoverflow.com/a/44633014


import tkinter as tk
from PIL import Image, ImageTk
from tkinter.filedialog import askopenfilename

import os
import json

from slideshow.SlideManager import SlideManager
from slideshow.SlideManager import Slide, ImageSlide, VideoSlide
import subprocess

import logging

# Logging
logger = logging.getLogger("kburns-slideshow-gui")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler( os.path.dirname(os.path.realpath(__file__)) + '/kburns-slideshow-gui.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class MyApp(tk.Tk):
    def __init__(self, title="Sample App", slideshow_config={}, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title(title)
        self.configure(background="Gray")
        
        # scale master frame to total Tk
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.geometry("300x400") #Width x Height

        master_frame = tk.Frame(self, bg='yellow')
        master_frame.grid(sticky=tk.NSEW)
        
        # scale subframes to width of master frame
        master_frame.columnconfigure(0, weight=1)
        # first row not changable
        master_frame.rowconfigure(0, weight=0)
        # scale second row to height of master frame
        master_frame.rowconfigure(1, weight=1)

        # Image Frame with fill parent (sticky=tk.NSEW)
        self.frame2 = ScrollFrame(master_frame, 100, "green")
        self.frame2.grid(row=0, column=0, sticky=tk.NSEW)
        
        
        # Bottom Frame with fill parent (sticky=tk.NSEW)
        frame3 = ScrollFrame(master_frame, 100, "blue")
        canvas3 = frame3.getCanvas()
        
        labelframe = tk.LabelFrame(canvas3, text="Options")
        #labelframe.grid(row=0, column=0, sticky=tk.NS)
        #labelframe.grid_rowconfigure(0, weight=1)
        #labelframe.grid_columnconfigure(0, weight=1)
        labelframe.pack_propagate(0) #Don't allow the widgets inside to determine the frame's width / height
        labelframe.pack(fill=tk.BOTH, expand=1) #Expand the frame to fill the root window
         
        left = tk.Label(labelframe, text="Test Content")
        left.grid(row=0, column=0, sticky=tk.NE)

        frame3.addFrame(labelframe)
        frame3.grid(row=1, column=0, sticky=tk.NSEW)
        
        
        frame4 = tk.Frame(master_frame, height=50, bg="red")
        button_save = tk.Button(frame4, text="Save Configuration", command=self.saveConfiguration)
        button_save.pack()

        frame4.grid(row=2, column=0, sticky=tk.NSEW)
        
        # Menu
        menubar = tk.Menu(self)
        
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.openFile)
        menubar.add_cascade(label="File", menu=filemenu)

        self.config(menu=menubar)
        
        self.slideshow_config = slideshow_config
    
    def onButtonClicked(self, button_id):
        print("Button" + str(button_id) + " is clicked!");
        
    def openFile(self):
        ftypes = [
            ('Slideshow config', '*.json')
        ]
        filename = askopenfilename(filetypes=ftypes)
        input_files = []
        audio_files = []
        try:
            with open(filename) as f:
                file_content = json.load(f)    
                
                # overwrite config with saved config
                if "config" in file_content:
                    self.slideshow_config.update(file_content["config"])
                    logger.debug("overwrite config")
                
                # get slides from loaded file
                if "slides" in file_content:
                    input_files = file_content["slides"]
                    logger.debug("get slides")
                
                if "audio" in file_content:
                    audio_files = file_content["audio"]
                    logger.debug("get audio")
                
            # Create Slide Manager
            self.sm = SlideManager(self.slideshow_config,input_files,audio_files)
        except:
            print("file must be a JSON file")
            logger.error("file %s must be a JSON file", filename)
        
        
        self.loadFileContent()
        
    def loadFileContent(self):
        canvas2 = self.frame2.getCanvas()
        
        images_frame = tk.Frame(canvas2, bg="red")
        
        basewidth = 100
        for i, slide in enumerate(self.sm.getSlides()):
            img_path = slide.file
            if isinstance(slide, VideoSlide):
                video_input_path = 'data\\1.mp4'
                img_path = 'temp\\thumbnail_%s.jpg' %(i)
                subprocess.call([self.slideshow_config["ffmpeg"], '-i', slide.file, '-ss', '00:00:00.000', '-vframes', '1', '-hide_banner', '-v', 'quiet', img_path])
        
            # https://stackoverflow.com/a/44978329
            img = Image.open(img_path)
            img.thumbnail((basewidth, basewidth))

            photo = ImageTk.PhotoImage(img)

            # https://stackoverflow.com/a/45733411
            # https://stackoverflow.com/questions/50787864/how-do-i-make-a-tkinter-button-in-an-list-of-buttons-return-its-index#comment88609106_50787933
            b = tk.Button(images_frame,image=photo, command=lambda c=i: self.onButtonClicked(c))
            b.image = photo # keep a reference
            b.grid(row=0, column=i, sticky=tk.NSEW)
        
        self.frame2.addFrame(images_frame)
        
    def saveConfiguration(self):
        self.sm.saveConfig("test.json")
        
class ScrollFrame(tk.Frame):
    def __init__(self, parent, height = 100, bg="white"):
        tk.Frame.__init__(self, parent)
        
        #self.grid(row=0, column=0)        
        # auto size
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(self, height=height, bg=bg)
        # fill parent (sticky=tk.NSEW)
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)
        #self.canvas.grid_rowconfigure(0, weight=1)
        #self.canvas.grid_columnconfigure(0, weight=1)
        
        # create vertical scrollbar
        vsbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        vsbar.grid(row=0, column=1, sticky=tk.NS)
        self.canvas.configure(yscrollcommand=vsbar.set)

        # create horizontal scrollbar
        hsbar = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.canvas.xview)
        hsbar.grid(row=1, column=0, sticky=tk.EW)
        self.canvas.configure(xscrollcommand=hsbar.set)
        
        
    def addFrame(self, frame):
        # create canvas window for the frame
        self.canvas_frame = self.canvas.create_window((0,0), window=frame, anchor=tk.NW)
        
        # update idletasks so that bounding box info is available
        frame.update_idletasks() 
        
        # update scrollregion to match frame content
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        
    def getCanvas(self):
        return self.canvas
        
if __name__ == "__main__":
    config = {}
    with open(os.path.dirname(os.path.realpath(__file__))+'/config.json') as config_file:
        config = json.load(config_file)   

    app = MyApp("kbvs", config)
    app.mainloop()