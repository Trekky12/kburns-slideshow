import subprocess
import os
import json
from .Slide import Slide
from .ImageSlide import ImageSlide
from .VideoSlide import VideoSlide
from .AudioFile import AudioFile

class SlideManager:

    def __init__(self, config, input_files, audio_files):
        self.slides = []
        self.background_tracks = []
        self.config = config
        self.tempfiles = []
        
        for position, file in enumerate(input_files):
        
            slide = None
            
            filename = file
            if isinstance(file, dict) and "file" in file:
                filename = file["file"]
             
            if isinstance(filename, str):
            
                # use parameters of saved file
                output_width = self.config["output_width"]
                if isinstance(file, dict) and "output_width" in file:
                    output_width = file["output_width"]
                
                output_height = self.config["output_height"]
                if isinstance(file, dict) and "output_height" in file:
                    output_height = file["output_height"]
                    
                slide_duration = self.config["slide_duration"]
                if isinstance(file, dict) and "slide_duration" in file:
                    slide_duration = file["slide_duration"]
                    
                fade_duration = self.config["fade_duration"]
                if isinstance(file, dict) and "fade_duration" in file:
                    fade_duration = file["fade_duration"]
                    
                zoom_direction = self.config["zoom_direction"]
                if isinstance(file, dict) and "zoom_direction" in file:
                    zoom_direction = file["zoom_direction"]
                    
                scale_mode = self.config["scale_mode"]
                if isinstance(file, dict) and "scale_mode" in file:
                    scale_mode = file["scale_mode"]
                    
                zoom_rate = self.config["zoom_rate"]
                if isinstance(file, dict) and "zoom_rate" in file:
                    zoom_rate = file["zoom_rate"]
                    
                fps = self.config["fps"]
                if isinstance(file, dict) and "fps" in file:
                    fps = file["fps"]
                
                extension = filename.split(".")[-1]
                
                if extension.lower() in [e.lower() for e in self.config["VIDEO_EXTENSIONS"]]:
                    slide = VideoSlide(filename, position, self.config["ffprobe"], output_width, output_height, fade_duration)
                if extension.lower() in [e.lower() for e in self.config["IMAGE_EXTENSIONS"]]:
                    slide = ImageSlide(filename, position, output_width, output_height, slide_duration, fade_duration, zoom_direction, scale_mode, zoom_rate, fps )
            
            if slide is not None:
                self.slides.append(slide)
        
        for file in audio_files:
        
            filename = file
            if isinstance(file, dict) and "file" in file:
                filename = file["file"]
        
            extension = filename.split(".")[-1]
            if extension.lower() in [e.lower() for e in self.config["AUDIO_EXTENSIONS"]]:
                audio = AudioFile(filename, self.config["ffprobe"] )
                self.background_tracks.append(audio)

    def getVideos(self):
        return [slide for slide in self.getSlides() if isinstance(slide, VideoSlide)]
    
    def getImageSlides(self):
        return [slide for slide in self.getSlides() if isinstance(slide, ImageSlide)]
    
    def getSlides(self):
        return self.slides + [self.slides[0]] if self.config["loopable"] else self.slides
        
    def getTotalDuration(self):
        return sum([slide.duration - slide.fade_duration for slide in self.getSlides()])+self.getSlides()[-1].fade_duration
            
    def getOffset(self, idx):
        return sum([slide.duration - slide.fade_duration for slide in self.getSlides()[:idx]])
        
    def getVideoFilterChains(self):
        # Base black image
        filter_chains = [
          "color=c=black:r=%s:size=%sx%s:d=%s[black]" %(self.config["fps"], self.config["output_width"], self.config["output_height"], self.getTotalDuration())
        ]
        
        for i, slide in enumerate(self.getSlides()):
        
            filters = slide.getFilter()
            
            if self.config["generate_temp"] and isinstance(slide, ImageSlide):
                tempvideo = "temp-kburns-%s.mp4" %(i)
                cmd = [
                    self.config["ffmpeg"], "-y", "-hide_banner", "-v", "quiet",
                    "-i \"%s\" " % (slide.file),
                    "-filter_complex", ",".join(slide.getFilter()),
                    "-crf", "0" ,"-preset", "ultrafast", "-tune", "stillimage",
                    "-c:v", "libx264", tempvideo
                ]

                # re-use existing temp file
                if not os.path.exists(tempvideo):
                    subprocess.call(" ".join(cmd))

                slide.file = tempvideo
                self.tempfiles.append(tempvideo)
                filters = []
            
            # Fade filter   
            if slide.fade_duration > 0:
                filters.append("fade=t=in:st=0:d=%s:alpha=%s" %(slide.fade_duration, 0 if i == 0 else 1))
                filters.append("fade=t=out:st=%s:d=%s:alpha=%s" %(slide.duration -slide.fade_duration, slide.fade_duration, 0 if i == len(self.getSlides()) - 1 else 1))
            else:
                filters.append("tpad=stop_duration=%s:color=black" %(slide.duration))

            # Time
            offset = self.getOffset(i)
            filters.append("setpts=PTS-STARTPTS+%s/TB" %(offset))

            # All together now
            filter_chains.append("[%s:v]" %(i) + ", ".join(filters) + "[v%s]" %(i)) 


        for i, slide in enumerate(self.getSlides()):
            input_1 = "ov%s" %(i-1) if i > 0 else "black"
            input_2 = "v%s" %(i)
            output = "out" if i == len(self.getSlides()) - 1 else "ov%s" %(i)
            overlay_filter = "%s" %(slide.getOverlay(i == len(self.getSlides()) - 1))
            
            filter_chains.append("[%s][%s]%s[%s]" %(input_1, input_2, overlay_filter, output))
            
        return filter_chains
        
    def getBackgroundTracks(self):
        return self.background_tracks
        
    def hasAudio(self):
        return len(self.background_tracks)> 0 or len([video for video in self.getVideos() if video.has_audio]) > 0
        
    def getAudioFilterChains(self):
        filter_chains = []

        # audio from video slides
        audio_tracks = []
        for slide in [slide for slide in self.getVideos() if slide.has_audio]:
            audio_tracks.append("[a%s]" %(slide.position))
            
            filters = []
            # Fade music in filter
            if slide.fade_duration > 0:
                filters.append("afade=t=in:st=0:d=%s" %(slide.fade_duration))
                filters.append("afade=t=out:st=%s:d=%s" %(slide.duration - slide.fade_duration, slide.fade_duration ))
            filters.append("adelay=%s|%s" %( int(self.getOffset(slide.position) *1000), int(self.getOffset(slide.position) *1000)))
            
            filter_chains.append("[%s:a] %s [a%s]" %(slide.position, ",".join(filters), slide.position))
        
        # background-tracks
        music_input_offset = len(self.getSlides())
        background_audio = ["[%s:a]" %(i+music_input_offset) for i, track in enumerate(self.background_tracks)]
        if len(background_audio) > 0:
            # merge background tracks
            filter_chains.append("%s concat=n=%s:v=0:a=1[background_audio]" %("".join(background_audio), len(self.background_tracks)))

            # extract background audio sections between videos
            background_sections = []
            # is it starting with a video or an image?
            section_start_slide = None if self.getSlides()[0].video else self.getSlides()[0]
            for slide in self.getSlides():
                # is it a video and we have a start value => end of this section
                if slide.video and slide.has_audio and section_start_slide is not None:
                    background_sections.append({ "start": self.getOffset(section_start_slide.position), "fade_in": section_start_slide.fade_duration, "end": self.getOffset(slide.position), "fade_out": slide.fade_duration })
                    section_start_slide = None
                # is it a image but the previous one was a video => start new section
                if not slide.video and section_start_slide is None:
                    section_start_slide = slide

            # the last section is ending with an image => end of section is end generated video
            if section_start_slide is not None:
                background_sections.append({ "start": self.getOffset(section_start_slide.position), "fade_in": section_start_slide.fade_duration, "end": self.getTotalDuration()-self.getSlides()[-1].fade_duration, "fade_out": self.getSlides()[-1].fade_duration })
               
               
            # split the background tracks in the necessary sections
            filter_chains.append("[background_audio]asplit=%s %s" %(len(background_sections), "".join(["[b%s]" %(i) for i, section in enumerate(background_sections)])))

            # fade background sections in/out
            for i, section in enumerate(background_sections):
                audio_tracks.append("[b%sf]" %(i))
                filter_chains.append("[b%s]afade=t=in:st=%s:d=%s,afade=t=out:st=%s:d=%s[b%sf]" %(i, section["start"], section["fade_in"], section["end"], section["fade_out"], i))

    

        # video audio and background sections should be merged     
        if len(audio_tracks) > 0:
            filter_chains.append("%s amix=inputs=%s[aout]" %("".join(audio_tracks), len(audio_tracks))) 
        
        return filter_chains
        
    def createVideo(self, output_file):
    
        if self.config["save"] is not None: 
            self.saveConfig(self.config["save"])
    
        filter_chains = self.getVideoFilterChains() + self.getAudioFilterChains()  
    
        # Run ffmpeg
        cmd = [ self.config["ffmpeg"], "-hide_banner", 
            "-y" if self.config["overwrite"] else "",
            # slides
            " ".join(["-i \"%s\" " %(slide.file) for slide in self.getSlides()]),
            " ".join(["-i \"%s\" " %(track.file) for track in self.getBackgroundTracks()]),
            # filters
            "-filter_complex \"%s\"" % (";".join(filter_chains)),
            # define duration
            # if video should be loopable, skip the start fade-in (-ss) and the end fade-out (video is stopped after the fade-in of the last image which is the same as the first-image)
            "-ss %s -t %s" %(self.getSlides()[0].fade_duration, self.getOffset(-1)) if self.config["loopable"] else "-t %s" %(self.getTotalDuration()),
            # define output
            "-map", "[out]:v",
            "-c:v", "libx264", 
            "-map [aout]:a" if self.hasAudio() else "",
            # audio compression and bitrate
            "-c:a", "aac" if self.hasAudio() else "",
            "-b:a", "160k" if self.hasAudio() else "",
            output_file
        ]  

        subprocess.call(" ".join(cmd))
        
        if self.config["delete_temp"]:
            for temp in self.tempfiles:
                os.remove(temp)
                
    def saveConfig(self, filename):
        content = {
            "config": {
                "output_width": self.config["output_width"],
                "output_height": self.config["output_height"],
                "slide_duration": self.config["slide_duration"],
                "fade_duration": self.config["fade_duration"],
                "fps": self.config["fps"],
                "zoom_rate": self.config["zoom_rate"],
                "zoom_direction": self.config["zoom_direction"],
                "scale_mode": self.config["scale_mode"],
                "loopable": self.config["loopable"],
                "overwrite": self.config["overwrite"],
                "generate_temp": self.config["generate_temp"],
                "delete_temp": self.config["delete_temp"]
            }, 
            "slides": [slide.getObject() for slide in self.slides],
            "audio":  [track.getObject() for track in self.getBackgroundTracks()]
        }
        with open('%s' %(filename), 'w') as file:
            json.dump(content, file, indent=4)