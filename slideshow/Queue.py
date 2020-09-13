#!/usr/bin/env python3

import os
import logging
import subprocess

logger = logging.getLogger("kburns-slideshow")

class Queue:

    def __init__(self, tempFileFolder, tempFilePrefix):
        self.tempFileFolder = tempFileFolder
        self.tempFilePrefix = tempFilePrefix
        self.queue = []
        
        if not os.path.exists(self.tempFileFolder):
            os.mkdir(self.tempFileFolder)
            logger.debug("Temporary directory %s created", self.tempFileFolder)
        
        # delete these files eventually
        self.tempFiles = []
        
    def addItem(self, inputs, filters, suffix):
        item = {"inputs": inputs, "filters": filters, "suffix": suffix}
        self.queue.append(item)
        
        return self.getOutputName(item)
        
    def getQueue(self):
        return self.queue
        
    def getFileName(self, item):
        return "%s%s.mp4" %(self.tempFilePrefix, item["suffix"])
        
    def getOutputName(self, item):
        return os.path.join(self.tempFileFolder, self.getFileName(item))
        
    def createTemporaryVideos(self, ffmpeg):
        for idx, item in enumerate(self.queue):
            print("Processing video %s/%s" %(idx, len(self.queue)))
            self.createTemporaryVideo(ffmpeg, item)
        
    def createTemporaryVideo(self, ffmpeg, item):

        if isinstance(item["filters"], list):
            filters = "%s" %(",".join(item["filters"]))
        else:
            filters = item["filters"]
        
        cmd = [
            ffmpeg, "-y", "-hide_banner", "-stats", "-v", "quiet",
            " ".join(["-i \"%s\" " % (i) for i in item["inputs"]]),
            "-filter_complex \"%s [out]\"" %(filters.replace("\n", " ")),
            #"-crf", "0" ,
            "-map [out]",
            "-preset", "ultrafast", 
            "-tune", "stillimage",
            "-c:v", "libx264", 
            self.getOutputName(item)
        ]
        
        # re-use existing temp file
        if not os.path.exists(self.getOutputName(item)):
            logger.debug("Create temporary video %s for file %s", self.getOutputName(item), ",".join(item["inputs"]))
            #logger.debug("Command: %s", " ".join(cmd))
            subprocess.call(" ".join(cmd), shell=True)
        else:
            logger.debug("Using existing temporary video %s for file %s", self.getOutputName(item), ",".join(item["inputs"]))

        self.tempFiles.append(self.getFileName(item))
        
    def clean(self):
        for temp in self.tempFiles:
            file = os.path.join(self.tempFileFolder, temp)
            os.remove(file)
            logger.debug("Delete %s", file)
        os.rmdir(self.tempFileFolder)