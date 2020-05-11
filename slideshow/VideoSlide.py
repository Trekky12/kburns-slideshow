#!/usr/bin/env python3

from .Slide import Slide
import subprocess

class VideoSlide(Slide):

    def __init__(self, ffmpeg_version, file, ffprobe, output_width, output_height, fade_duration = 1, title = None, fps = 60, overlay_text = None, transition = "random", force_no_audio = False, video_start = None, video_end = None):
        duration = subprocess.check_output(["%s" %(ffprobe), "-show_entries", "format=duration", "-v", "error", "-of", "default=noprint_wrappers=1:nokey=1", file]).decode()        
        duration = float(duration)
        
        super().__init__(ffmpeg_version, file, output_width, output_height, duration, fade_duration, fps, title, overlay_text, transition)
        
        audio = subprocess.check_output(["%s" %(ffprobe), "-select_streams", "a", "-show_entries", "stream=codec_type", "-v", "error", "-of",  "default=noprint_wrappers=1:nokey=1", file]).decode()
        self.video_has_audio = "audio" in str(audio)
        self.has_audio = self.video_has_audio
        
        width = subprocess.check_output(["%s" %(ffprobe), "-select_streams", "v", "-show_entries", "stream=width", "-v", "error", "-of" ,"default=noprint_wrappers=1:nokey=1", file]).decode()
        self.width = int(width)
        
        height = subprocess.check_output(["%s" %(ffprobe), "-select_streams", "v", "-show_entries", "stream=height", "-v", "error", "-of", "default=noprint_wrappers=1:nokey=1", file]).decode()
        self.height = int(height)
        
        self.ratio = self.width/self.height
        
        self.setForceNoAudio(force_no_audio)
        
        self.is_trimmed = False
        self.start = video_start if video_start is not None else None
        self.end = video_end if video_end is not None and video_end < self.duration else None
        self.calculateDurationAfterTrimming()
    
    def calculateDurationAfterTrimming(self):
        if self.start is not None or self.end is not None:
            self.is_trimmed = True
            
            # calculate new duration
            start = self.start if self.start is not None else 0
            end = self.end if self.end is not None else self.duration
            duration = end - start
            
            self.setDuration(duration)
        else:
            self.is_trimmed = False
        
    def setForceNoAudio(self, force_no_audio):
        self.force_no_audio = force_no_audio
        if force_no_audio:
            self.has_audio = False
        else:
            self.has_audio = self.video_has_audio
        
    def getFilter(self):
        width, height = [self.output_width, -1]
        if self.ratio < self.output_ratio:
           width, height = [-1, self.output_height]

        filters = []
        filters.append("scale=w=%s:h=%s" %(width, height))
        filters.append("fps=%s" %(self.fps))
        filters.append("pad=%s:%s:(ow-iw)/2:(oh-ih)/2" %(self.output_width, self.output_height))
        
        if self.is_trimmed:
            trim = []
            if self.start is not None:
                trim.append("start=%s" %(self.start))
            if self.end is not None:
                trim.append("end=%s" %(self.end))
                
            filters.append("trim=%s,setpts=PTS-STARTPTS" %(":".join(trim)))
        
        return [",".join(filters)]
        
    def getAudioFilter(self):
        if self.is_trimmed:
            trim = []
            if self.start is not None:
                trim.append("start=%s" %(self.start))
            if self.end is not None:
                trim.append("end=%s" %(self.end))
                
            return "atrim=%s,asetpts=PTS-STARTPTS" %(":".join(trim))
            
        return None
        
    def getObject(self, config):
        object = super().getObject(config)
        
        object["force_no_audio"] = self.force_no_audio
        
        if self.start is not None:
            object["start"] = self.start
        
        if self.end is not None:
            object["end"] = self.end

        return object