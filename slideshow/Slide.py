import pkgutil
import random

class Slide:

    def __init__(self, file, position, output_width, output_height, duration, fade_duration = 1, title = None, overlay_text = None, transition = "random"):
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
        
        if transition == "random":
            self.transition = random.choice(self.getEffects())
        else:
            self.transition = transition if transition in self.getEffects() else None
        
    def getFilter(self):
        return
        
    def getObject(self, config):
        object = {
            "file": self.file
        }
        if self.title is not None:
            object["title"] = self.title
            
        if self.overlay_text is not None:
            object["overlay"] = self.overlay_text
            
        if self.transition != config["transition"]:
            object["transition"] = self.transition
            
        return object
        
    def getEffects(self):
        return [package_name for importer, package_name, _ in pkgutil.iter_modules(["slideshow/effects"])]