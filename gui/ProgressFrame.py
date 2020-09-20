import tkinter as tk
from tkinter import ttk

import time
import threading

import logging

logger = logging.getLogger("kburns-slideshow")


class ProgressFrame(tk.Toplevel):
    def __init__(self, parent, **options):
        tk.Toplevel.__init__(self, options)
        
        self.title("Processing")
        self.resizable(False, False)
        
        self.progress_var1 = tk.DoubleVar()
        self.progress_var2 = tk.DoubleVar()
        
        self.progress_var1.set(0)
        self.progress_var2.set(0)

        self.is_cancelled  = False
        self.ffmpeg_process = None
        
        self.protocol("WM_DELETE_WINDOW", self.disable_event)
        self.bind("<Destroy>", self._destroy)

    def create(self, has_temporary_files = False, queue_length = 100, frame_number = 100):
    
        if has_temporary_files:
            tk.Label(self, text="Temporary Video Files").grid(row=0,column=0, sticky=tk.W)

            progress_bar1 = ttk.Progressbar(self, variable=self.progress_var1, maximum=queue_length, length=400)
            progress_bar1.grid(row=1, column=0, sticky=tk.NSEW, padx=4, pady=4)
                
        tk.Label(self, text="Final Video").grid(row=3,column=0, sticky=tk.W)
        progress_bar2 = ttk.Progressbar(self, variable=self.progress_var2, value=0, maximum=100, mode = 'indeterminate', length=400)
        progress_bar2.grid(row=4, column=0, sticky=tk.NSEW, padx=4, pady=4)
        
        buttonCancel = tk.Button(self, text="Cancel", command=(lambda: self.cancel()))
        buttonCancel.grid(row=5, column=0, sticky=tk.NSEW, padx=4, pady=4)
    
    def startProgressBar(self):
        progressBarThread = threading.Thread(target=self.processProgressBar, daemon = True)
        progressBarThread.start()
        
    def processProgressBar(self):
        while True:
            for i in [0,20,40,60,80,100,80,60,40,20]:
                self.progress_var2.set(i)
                self.update_idletasks() 
                time.sleep(0.5)
                    
    def disable_event(self):
        pass
        
    def _destroy(self, event):
        self.cancel()
    
    def cancel(self):
        logger.info("Cancel FFMPEG")
        self.is_cancelled = True
        if self.ffmpeg_process is not None:
            try:
                self.ffmpeg_process.communicate(b'q')
                self.ffmpeg_process = None
            except Exception as e:
                logger.info("Error FFMPEG cancel, Error: %s" %(e))
        
    def setFinalVideoProcess(self, p):
        self.ffmpeg_process = p