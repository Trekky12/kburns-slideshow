# https://stackoverflow.com/a/49681192

import tkinter as tk
import logging

logger = logging.getLogger("kburns-slideshow-gui")


class ScrollFrame(tk.Frame):
    def __init__(self, parent, height = 100, bg=None):
        tk.Frame.__init__(self, parent)
          
        # auto size
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(self, height=height, bg=bg, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)
        
        # create vertical scrollbar
        vsbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        vsbar.grid(row=0, column=1, sticky=tk.NS)
        self.canvas.configure(yscrollcommand=vsbar.set)

        # create horizontal scrollbar
        hsbar = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.canvas.xview)
        hsbar.grid(row=1, column=0, sticky=tk.EW)
        self.canvas.configure(xscrollcommand=hsbar.set)
        
    def addFrame(self, frame, anchor = tk.NW):
        # create canvas window for the frame
        self.canvas_frame = self.canvas.create_window((0,0), window=frame, anchor=anchor)
        
        # update idletasks so that bounding box info is available
        frame.update_idletasks() 
        
        # update scrollregion to match frame content
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        
    def getCanvas(self):
        return self.canvas
        
    def clear(self):
        self.canvas.delete('all')