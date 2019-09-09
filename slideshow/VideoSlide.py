#!/usr/bin/env python3

from .Slide import Slide
import subprocess

class VideoSlide(Slide):

    def __init__(self, file, ffprobe, output_width, output_height, fade_duration = 1, title = None, fps = 60, overlay_text = None, transition = "random", force_no_audio = False):
        
        duration = subprocess.check_output("%s -show_entries format=duration -v error -of default=noprint_wrappers=1:nokey=1 \"%s\"" %(ffprobe, file)).decode()
        width = subprocess.check_output("%s -select_streams v -show_entries stream=width -v error -of default=noprint_wrappers=1:nokey=1 \"%s\"" %(ffprobe, file)).decode()
        height = subprocess.check_output("%s -select_streams v -show_entries stream=height -v error -of default=noprint_wrappers=1:nokey=1 \"%s\"" %(ffprobe, file)).decode()
        
        super().__init__(file, output_width, output_height, float(duration), fade_duration, fps, title, overlay_text, transition)
        
        audio = subprocess.check_output("%s -select_streams a -show_entries stream=codec_type -v error -of default=noprint_wrappers=1:nokey=1 \"%s\"" %(ffprobe, file)).decode()
        has_audio = "audio" in str(audio)
        
        self.has_audio = False if force_no_audio else has_audio
        self.width = int(width)
        self.height = int(height)
        self.ratio = self.width/self.height
        
    def getFilter(self):
        width, height = [self.output_width, -1]
        if self.ratio < self.output_ratio:
           width, height = [-1, self.output_height]

        return ["scale=w=%s:h=%s,fps=%s, pad=%s:%s:(ow-iw)/2:(oh-ih)/2" %(width, height, self.fps, self.output_width, self.output_height)]