#!/usr/bin/env python3

import os
import logging
import subprocess

logger = logging.getLogger("kburns-slideshow")

class Queue:

    def __init__(self, tempFilePrefix):
        self.tempFilePrefix = tempFilePrefix
        self.queue = []
        
        # delete these files eventually
        self.tempFiles = []
        
    def addItem(self, inputs, filters, suffix):
        item = {"inputs": inputs, "filters": filters, "suffix": suffix}
        self.queue.append(item)
        
        return self.getFileName(item)
        
    def getQueue(self):
        return self.queue
        
    def getFileName(self, item):
        return "%s%s.mp4" %(self.tempFilePrefix, item["suffix"])
        
    def createTemporaryVideos(self, ffmpeg):
        for item in self.queue:
            self.createTemporaryVideo(ffmpeg, item)
        
    def createTemporaryVideo(self, ffmpeg, item):

        if isinstance(item["filters"], list):
            filters = "%s" %(",".join(item["filters"]))
        else:
            filters = item["filters"]
        
        cmd = [
            ffmpeg, "-y", "-hide_banner", "-stats", "-v", "quiet",
            " ".join(["-i \"%s\" " % (i) for i in item["inputs"]]),
            "-filter_complex \"%s [out]\"" %(filters),
            #"-crf", "0" ,
            "-map [out]",
            "-preset", "ultrafast", 
            "-tune", "stillimage",
            "-c:v", "libx264", 
            self.getFileName(item)
        ]
        
        #print(" ".join(cmd))
        
        # re-use existing temp file
        if not os.path.exists(self.getFileName(item)):
            logger.debug("Create temporary video %s for file %s", self.getFileName(item), ",".join(item["inputs"]))
            subprocess.call(" ".join(cmd))
        else:
            logger.debug("Using existing temporary video %s for file %s", self.getFileName(item), ",".join(item["inputs"]))

        self.tempFiles.append(self.getFileName(item))
        
    def clean(self):
        for temp in self.tempFiles:
            os.remove(temp)
            logger.debug("Delete %s", temp)