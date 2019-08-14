class Slide:

    def __init__(self, file, position, output_width, output_height, duration, fade_duration = 1, title = None, overlay_text = None):
        self.file = file
        self.position = position
        self.video = False
        self.has_audio = False
        self.output_width = output_width
        self.output_height = output_height
        self.duration = duration
        self.fade_duration = fade_duration
        self.title = title
        self.overlay_text = overlay_text
        self.output_ratio = self.output_width / self.output_height
        
    def getFilter(self):
        return
        
    def getOverlay(self, isLast):
        return
        
    def getObject(self):
        object = {
            "file": self.file
        }
        if self.title is not None:
            object["title"] = self.title
            
        if self.overlay_text is not None:
            object["overlay"] = self.overlay_text
            
        return object