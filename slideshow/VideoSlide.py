from .Slide import Slide
import subprocess

class VideoSlide(Slide):

    def __init__(self, file, position, ffprobe, output_width, output_height, fade_duration = 1, title = None, fps = 60, overlay_text = None, transition = "random"):
        
        duration = subprocess.check_output("%s -show_entries format=duration -v error -of default=noprint_wrappers=1:nokey=1 %s" %(ffprobe, file))
        has_audio = subprocess.check_output("%s -select_streams a -show_entries stream=codec_type -v error -of default=noprint_wrappers=1:nokey=1 %s" %(ffprobe, file))
        width = subprocess.check_output("%s -select_streams v -show_entries stream=width -v error -of default=noprint_wrappers=1:nokey=1 %s" %(ffprobe, file))
        height = subprocess.check_output("%s -select_streams v -show_entries stream=height -v error -of default=noprint_wrappers=1:nokey=1 %s" %(ffprobe, file))
        
        super().__init__(file, position, output_width, output_height, float(duration), fade_duration, title, overlay_text, transition)
        self.video = True
        self.has_audio = "audio" in str(has_audio)
        self.fps = fps
        self.width = int(width)
        self.height = int(height)
        self.ratio = self.width/self.height
        
    def getFilter(self):
        width, height = [self.output_width, -1]
        if self.ratio < self.output_ratio:
           width, height = [-1, self.output_height]

        return ["scale=w=%s:h=%s,fps=%s, pad=%s:%s:(ow-iw)/2:(oh-ih)/2" %(width, height, self.fps, self.output_width, self.output_height)]