from .Slide import Slide
import subprocess

class VideoSlide(Slide):

    def __init__(self, file, position, ffprobe, output_width, output_height, fade_duration = 1, title = None):
        
        duration = subprocess.check_output("%s -show_entries format=duration -v error -of default=noprint_wrappers=1:nokey=1 %s" %(ffprobe, file))
        has_audio = subprocess.check_output("%s -select_streams a -show_entries stream=codec_type -v error -of default=noprint_wrappers=1:nokey=1 %s" %(ffprobe, file))
        
        super().__init__(file, position, output_width, output_height, float(duration), fade_duration, title)
        self.video = True
        self.has_audio = "audio" in str(has_audio)
        
    def getFilter(self):
        return ["scale=w=%s:h=-1" %(self.output_width)]
        
    def getOverlay(self, isLast):
        return "overlay=(W-w)/2:(H-h)/2%s" %(":format=yuv420" if isLast else "")