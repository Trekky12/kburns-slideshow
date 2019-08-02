import subprocess

class AudioFile:

    def __init__(self, file, ffprobe):
    
        self.file = file
        
        duration = subprocess.check_output("%s -show_entries format=duration -v error -of default=noprint_wrappers=1:nokey=1 %s" %(ffprobe, file))
        self.duration = float(duration)
        
    def getObject(self):
        return self.file