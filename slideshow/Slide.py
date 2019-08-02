class Slide:

    def __init__(self, file, position, output_width, output_height, duration, fade_duration = 1):
        self.file = file
        self.position = position
        self.video = False
        self.has_audio = False
        self.output_width = output_width
        self.output_height = output_height
        self.duration = duration
        self.fade_duration = fade_duration

        
    def getFilter(self):
        return
        
    def getOverlay(self, isLast):
        return
        
    def getObject(self):
        return {
            "file": self.file
        }
    