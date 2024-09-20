#!/usr/bin/env python3

import os
import logging
import subprocess

logger = logging.getLogger("kburns-slideshow")


class Queue:

    def __init__(self, ffmpeg_version, tempFileFolder, tempFilePrefix):
        self.tempFileFolder = tempFileFolder
        self.tempFilePrefix = tempFilePrefix
        self.ffmpeg_version = ffmpeg_version
        self.init()

    def init(self):
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

    def getQueueLength(self):
        return len(self.queue)

    def getFileName(self, item, extension="mp4"):
        return "%s%s.%s" % (self.tempFilePrefix, item["suffix"], extension)

    def getOutputName(self, item, extension="mp4"):
        return os.path.join(self.tempFileFolder, self.getFileName(item, extension))

    def createTemporaryVideo(self, ffmpeg, item, parameters, codec, fps):

        if isinstance(item["filters"], list):
            filters = "%s" % (",".join(item["filters"]))
        else:
            filters = item["filters"]

        temp_filter_script = self.getOutputName(item, "txt")
        with open('%s' % (temp_filter_script), 'w', newline='\n') as file:
            file.write("%s [out]" % (filters))

        cmd = [
            ffmpeg, "-y", "-hide_banner", "-stats", "-v", "warning",
            " ".join(["-i \"%s\" " % (i) for i in item["inputs"]]),
            "-filter_complex_script \"%s\"" % (temp_filter_script)
            if self.ffmpeg_version[0] < 7
            else "-/filter_complex \"%s\"" % (temp_filter_script),
            # "-crf", "0" ,
            "-map [out]",
            # "-preset", "ultrafast",
            # "-tune", "stillimage",
            parameters,
            "-r %s" % fps,
            # "-c:v", "libx264",
            "-c:v %s" % codec,
            "\"%s\"" % self.getOutputName(item)
        ]

        # re-use existing temp file
        if not os.path.exists(self.getOutputName(item)):
            logger.debug("Create temporary video %s for file %s",
                         self.getOutputName(item), ",".join(item["inputs"]))
            # logger.debug("Command: %s", " ".join(cmd))
            subprocess.call(" ".join(cmd), shell=True)
        else:
            logger.debug("Using existing temporary video %s for file %s",
                         self.getOutputName(item), ",".join(item["inputs"]))

        if os.path.exists(self.getOutputName(item)):
            self.tempFiles.append(self.getFileName(item))
            self.tempFiles.append(self.getFileName(item, "txt"))
            return self.getOutputName(item)

        return None

    def clean(self, delete_temp=True):
        if delete_temp:
            for temp in self.tempFiles:
                file = os.path.join(self.tempFileFolder, temp)
                os.remove(file)
                logger.debug("Delete %s", file)
            # os.rmdir(self.tempFileFolder)
        self.init()
