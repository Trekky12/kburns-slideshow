import subprocess

class AudioFile:

    def __init__(self, file, ffprobe):
    
        self.file = file
        
        duration = subprocess.check_output("%s -show_entries format=duration -v error -of default=noprint_wrappers=1:nokey=1 %s" %(ffprobe, file))
        self.duration = float(duration)
        
    def getOnsets(self, aubio):
        aubioonset = subprocess.check_output("%s -i %s -O %s" %(aubio, self.file, "kl"), stderr=subprocess.DEVNULL).decode().splitlines()      
        return aubioonset
        
    def getObject(self):
        return self.file