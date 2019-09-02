import pkgutil
import random
import os

class Slide:

    def __init__(self, file, output_width, output_height, duration, fade_duration = 1, fps = 60, title = None, overlay_text = None, transition = "random"):
        self.file = file
        self.has_audio = False
        self.output_width = output_width
        self.output_height = output_height
        self.duration = duration
        # fade-out duration (= fade-in duration of next slide)
        self.fade_duration = fade_duration
        self.title = title
        self.overlay_text = overlay_text
        self.output_ratio = self.output_width / self.output_height
        self.fps = fps
        
        if transition == "random":
            self.transition = random.choice(self.getEffects())
        else:
            self.transition = transition if transition in self.getEffects() else None
        
        self.splits = []
        
    def getDuration(self):
        return self.duration
        
    def getFilter(self):
        return
        
    def getObject(self, config):
        object = {
            "file": self.file
        }
        
        if self.duration != config["slide_duration"]:
            object["slide_duration"] = self.duration
            
        if self.fade_duration != config["fade_duration"]:
            object["fade_duration"] = self.fade_duration
            
        if self.title is not None:
            object["title"] = self.title
            
        if self.overlay_text is not None:
            object["overlay"] = self.overlay_text
            
        if self.transition != config["transition"]:
            object["transition"] = self.transition
            
        return object
        
    def getEffects(self):
        return [package_name for importer, package_name, _ in pkgutil.iter_modules([os.path.dirname(os.path.realpath(__file__))+"/effects"])]