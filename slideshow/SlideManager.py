import subprocess
import os
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
            extension = file.split(".")[-1]
            slide = None
            if extension in self.config["VIDEO_EXTENSIONS"]:
                slide = VideoSlide(file, position, self.config["ffprobe"], self.config["output_width"], self.config["output_height"])
            elif extension in self.config["IMAGE_EXTENSIONS"]:
                slide = ImageSlide(file, position, self.config["output_width"], self.config["output_height"], self.config["slide_duration"], self.config["fade_duration"], self.config["zoom_direction"], self.config["scale_mode"], self.config["zoom_rate"], self.config["fps"] )
            
            if slide is not None:
                self.slides.append(slide)
        
        for file in audio_files:
            extension = file.split(".")[-1]
            if extension in self.config["AUDIO_EXTENSIONS"]:
                audio = AudioFile(file, self.config["ffprobe"] )
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
                    "-i", slide.file,
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
    
        filter_chains = self.getVideoFilterChains() + self.getAudioFilterChains()  
    
        # Run ffmpeg
        cmd = [ self.config["ffmpeg"], "-hide_banner", 
            "-y" if self.config["overwrite"] else "",
            # slides
            " ".join(["-i %s" %(slide.file) for slide in self.getSlides()]),
            " ".join(["-i %s" %(track.file) for track in self.getBackgroundTracks()]),
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