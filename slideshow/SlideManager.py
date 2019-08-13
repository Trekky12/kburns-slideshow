import subprocess
import os
import json
import sys
import logging
import datetime
import re
from .Slide import Slide
from .ImageSlide import ImageSlide
from .VideoSlide import VideoSlide
from .AudioFile import AudioFile

logger = logging.getLogger("kburns-slideshow")

class SlideManager:

    def __init__(self, config, input_files, audio_files):
        self.slides = []
        self.background_tracks = []
        self.config = config
        self.tempfiles = []
        
        logger.debug("Init SlideManager")
        for position, file in enumerate(input_files):
            
            logger.debug("Slide: %d, File: %s", position, file)
            
            slide = None
            
            filename = file
            if isinstance(file, dict) and "file" in file:
                filename = file["file"]
             
            if isinstance(filename, str):
            
                output_width = self.config["output_width"]
                output_height = self.config["output_height"]
                fps = self.config["fps"]
                    
                # use parameters of saved file
                slide_duration = self.config["slide_duration"]
                if isinstance(file, dict) and "slide_duration" in file:
                    slide_duration = file["slide_duration"]
                    
                slide_duration_min = self.config["slide_duration_min"]
                if isinstance(file, dict) and "slide_duration_min" in file:
                    slide_duration_min = file["slide_duration_min"]
                    
                fade_duration = self.config["fade_duration"]
                if isinstance(file, dict) and "fade_duration" in file:
                    fade_duration = file["fade_duration"]
                    
                zoom_direction = self.config["zoom_direction"]
                if isinstance(file, dict) and "zoom_direction" in file:
                    zoom_direction = file["zoom_direction"]
                    
                zoom_rate = self.config["zoom_rate"]
                if isinstance(file, dict) and "zoom_rate" in file:
                    zoom_rate = file["zoom_rate"]
                    
                scale_mode = self.config["scale_mode"]
                if isinstance(file, dict) and "scale_mode" in file:
                    scale_mode = file["scale_mode"]
                
                title = None
                if isinstance(file, dict) and "title" in file:
                    title = file["title"]
                    
                overlay_text = None
                if isinstance(file, dict) and "overlay" in file:
                    overlay_text = file["overlay"]
                    
                extension = filename.split(".")[-1]
                
                if extension.lower() in [e.lower() for e in self.config["VIDEO_EXTENSIONS"]]:
                    slide = VideoSlide(filename, position, self.config["ffprobe"], output_width, output_height, fade_duration, title, fps, overlay_text)
                if extension.lower() in [e.lower() for e in self.config["IMAGE_EXTENSIONS"]]:
                    slide = ImageSlide(filename, position, output_width, output_height, slide_duration, slide_duration_min, fade_duration, zoom_direction, scale_mode, zoom_rate, fps, title, overlay_text)
            
            if slide is not None:
                self.slides.append(slide)
                logger.debug("added valid video/image file")
        
        for file in audio_files:
            
            logger.debug("Audiofile: %s", file)
            
            filename = file
            if isinstance(file, dict) and "file" in file:
                filename = file["file"]
        
            extension = filename.split(".")[-1]
            if extension.lower() in [e.lower() for e in self.config["AUDIO_EXTENSIONS"]]:
                audio = AudioFile(filename, self.config["ffprobe"] )
                self.background_tracks.append(audio)
                logger.debug("added valid audio file")

    def getVideos(self):
        return [slide for slide in self.getSlides() if isinstance(slide, VideoSlide)]
    
    def getImageSlides(self):
        return [slide for slide in self.getSlides() if isinstance(slide, ImageSlide)]
    
    def getSlides(self):
        if self.config["loopable"]:
            return self.slides + [self.slides[0]]
        return self.slides
        
    def getTotalDuration(self):
        return sum([slide.duration - slide.fade_duration for slide in self.getSlides()])+self.getSlides()[-1].fade_duration
    
    def getVideoAudioDuration(self):
        return sum([slide.duration for slide in self.getVideos() if slide.has_audio])
    
    def getAudioDuration(self):
        return sum([slide.duration for slide in self.getBackgroundTracks()])
            
    def getOffset(self, idx):
        return sum([slide.duration - slide.fade_duration for slide in self.getSlides()[:idx]])
        
    def getVideoFilterChains(self, burnSubtitles = False, srtFilename = ""):
    
        logger.debug("get Video Filter Chains")
        
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
                    #"-crf", "0" ,
                    "-preset", "ultrafast", 
                    "-tune", "stillimage",
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

            # Overlay Text (e.g. Intro)
            if slide.overlay_text is not None and "title" in slide.overlay_text:
                duration = slide.overlay_text["duration"] if "duration" in slide.overlay_text else 1
                font = ":font='%s'" %(slide.overlay_text["font"]) if "font" in slide.overlay_text else ""
                font_size = slide.overlay_text["font_size"] if "font_size" in slide.overlay_text else 150
                transition_x = slide.overlay_text["transition_x"] if "transition_x" in slide.overlay_text else "center"
                
                # fixed text in the middle
                if transition_x == "center":
                    x = "(main_w/2-text_w/2)"
                # scroll from left to right till the middle of the image in half of the duration time
                elif transition_x == "left-in":
                    x = "'if(lte(x,(main_w/2-text_w/2)),t*(main_w/2-text_w/2)/(%s/2),(main_w/2-text_w/2))'" %(duration)
                # same but from right to left
                elif transition_x == "right-in":
                    x = "'if(gte(x,(main_w/2-text_w/2)),main_w-t*(main_w/2-text_w/2)/(%s/2),(main_w/2-text_w/2))'" %(duration)

                y = "(main_h/2-text_h/2)"
                
                filters.append("drawbox=w=iw:h=ih:color=black@0.8:t=fill:enable='between(t,0,%s)'" %(duration))
                filters.append("drawtext=text='%s':line_spacing=20:fontsize=%s: fontcolor=white:y=%s:x=%s:borderw=1%s:enable='between(t,0,%s)'" % (slide.overlay_text["title"], font_size, y, x, font , duration))
                
                if isinstance(slide, ImageSlide):
                    slide.slide_duration_min = slide.slide_duration_min + duration
            # Time
            offset = self.getOffset(i)
            filters.append("setpts=PTS-STARTPTS+%s/TB" %(offset))

            # All together now
            filter_chains.append("[%s:v]" %(i) + ", ".join(filters) + "[v%s]" %(i)) 


        for i, slide in enumerate(self.getSlides()):
            isLastSlide = i == len(self.getSlides()) - 1
            input_1 = "ov%s" %(i-1) if i > 0 else "black"
            input_2 = "v%s" %(i)
            output = "out" if isLastSlide else "ov%s" %(i)
            overlay_filter = "%s" %(slide.getOverlay(isLastSlide))
            
            subtitles = ""
            # Burn subtitles to last element
            if burnSubtitles and self.hasSubtitles() and isLastSlide:
                subtitles = ",subtitles=%s" %(srtFilename)
                
            filter_chains.append("[%s][%s]%s%s[%s]" %(input_1, input_2, overlay_filter, subtitles, output))
            
        return filter_chains
        
    def getBackgroundTracks(self):
        return self.background_tracks
        
    def hasAudio(self):
        return len(self.background_tracks)> 0 or len([video for video in self.getVideos() if video.has_audio]) > 0
        
    def hasSubtitles(self):
        return len([slide for slide in self.getSlides() if slide.title is not None]) > 0        
        
    def getAudioFilterChains(self):
    
        logger.debug("get Audio Filter Chains")
        
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
               
            if len(background_sections) > 0:                
                # merge background tracks
                filter_chains.append("%s concat=n=%s:v=0:a=1[background_audio]" %("".join(background_audio), len(self.background_tracks)))
            
                # split the background tracks in the necessary sections
                filter_chains.append("[background_audio]asplit=%s %s" %(len(background_sections), "".join(["[b%s]" %(i) for i, section in enumerate(background_sections)])))

                # fade background sections in/out
                for i, section in enumerate(background_sections):
                    audio_tracks.append("[b%sf]" %(i))
                    filter_chains.append("[b%s]afade=t=in:st=%s:d=%s,afade=t=out:st=%s:d=%s[b%sf]" %(i, section["start"], section["fade_in"], section["end"], section["fade_out"], i))
            else:
                logger.debug("no background section")
        else:
            logger.debug("no background music")
    
        # video audio and background sections should be merged     
        if len(audio_tracks) > 0:
            filter_chains.append("%s amix=inputs=%s[aout]" %("".join(audio_tracks), len(audio_tracks))) 
        else:
            logger.debug("no audio track")    
        
        return filter_chains
        
    def getDurationsFromAudio(self):
        
        logger.debug("get Durations from Audio Files")
        
        onsets = []
        offset = 0
        for track in self.getBackgroundTracks():
            # add beginning of track
            onsets.append(0+offset)
            # get onsets of track
            onsets = onsets + [float(onset)+offset for onset in track.getOnsets(self.config["aubio"])]
            # next track has the offsets after the current
            offset = offset + track.duration
        
        logger.debug("Timestamps: %s", onsets)
        
        durations = []
        last_timestamp = 0;
        for timestamp in onsets:
            diff = timestamp - last_timestamp
            if diff > 0:
                durations.append(diff)
                last_timestamp = timestamp
        
        return durations
        
    def adjustDurationsFromAudio(self):
        
        logger.debug("adjust slide durations")
        
        durations = self.getDurationsFromAudio()
        
        logger.debug("Durations: %s", durations)
        logger.debug("Slide durations (before): %s", [slide.duration for slide in self.getSlides()])
        
        # change slide durations
        duration_idx = 0
        for i, slide in enumerate(self.getSlides()):
            # is there a duration available?
            if not slide.has_audio and duration_idx < len(durations):
            
                duration = durations[duration_idx]

                if isinstance(slide, VideoSlide):
                    # video is longer than the duration to the next onset => skip to matching onset
                    while slide.duration > duration: 
                        if (duration_idx+1) < len(durations):
                            duration = duration + durations[duration_idx+1]
                            duration_idx = duration_idx+1
                        else:
                            duration = slide.duration

                    # next onset is after the video
                    if duration > slide.duration:
                        durations[duration_idx] = duration-slide.duration

                else:
                    # the duration to the next onset is to short, 
                    # accumulate the durations until the minimum duration is reached
                    while duration < slide.slide_duration_min:
                        # is the music long enough to append something
                        if (duration_idx+1) < len(durations):
                            duration = duration + durations[duration_idx+1]
                            duration_idx = duration_idx+1
                        # there is no more to add, so change it to the slide duration
                        else:
                            duration = slide.duration
                    
                    # the next onset is earlier than the initial slide duration => set the new duration
                    if duration < slide.duration:
                        slide.duration = duration
                        duration_idx = duration_idx+1
                    
                    # next onset is later than the initial slide duration, so don't change the slide duration 
                    # but subtract the slide duration from the expected duration
                    # so the next slide duration is considering this
                    else:
                        durations[duration_idx] = duration-slide.duration

        
        logger.debug("Slide durations (after): %s", [slide.duration for slide in self.getSlides()])
        
        # onsets
        slide_timestamps = [ sum([slide.duration for slide in self.getSlides()[:i+1] if not slide.has_audio]) for i, s in enumerate(self.getSlides()) if not s.has_audio ]
        logger.debug("Onsets of slides: %s", slide_timestamps)
        
    def createVideo(self, output_file):
        logger.info("Create video %s", output_file)
        
        # check if it is okay to have a shorter background track
        video_duration = self.getTotalDuration()
        audio_duration = self.getAudioDuration() + self.getVideoAudioDuration()
        if len(self.background_tracks)> 0 and audio_duration < video_duration:
            print("Background track is shorter than video length!")
            logger.info("Background track (%s) is shorter than video length (%s)!", audio_duration, video_duration)
            
            if not input("Are you sure this is fine? (y/n): ").lower().strip()[:1] == "y": 
                sys.exit(1)
    
        # Save configuration
        if self.config["save"] is not None: 
            self.saveConfig(self.config["save"])
            
        # Subtitles
        burnSubtitles = False if "mkv" in output_file.lower() else True
        srtInput = len(self.getSlides()) + len(self.getBackgroundTracks())
        srtFilename = "temp-kburns-subs.srt"
        if self.hasSubtitles():
            self.createSubtitles(srtFilename)

        # Filters
        filter_chains = self.getVideoFilterChains(burnSubtitles, srtFilename) + self.getAudioFilterChains()   
        
        temp_filter_script = "temp-kburns-video-script.txt"
        with open('%s' %(temp_filter_script), 'w') as file:
            file.write(";\n".join(filter_chains))
            
        # Get Frames
        frames = round(sum([slide.duration*self.config["fps"] for slide in self.getSlides()]))
        print("Number of Frames: %s" %(frames))
    
        # Run ffmpeg
        cmd = [ self.config["ffmpeg"], 
            "-hide_banner", 
            #"-v quiet",
            "-stats",
            "-y" if self.config["overwrite"] else "",
            # slides
            " ".join(["-i \"%s\" " %(slide.file) for slide in self.getSlides()]),
            " ".join(["-i \"%s\" " %(track.file) for track in self.getBackgroundTracks()]),
            # subtitles (only mkv)
            "-i %s" %(srtFilename) if self.hasSubtitles() and not burnSubtitles else "",
            # filters
            #"-filter_complex \"%s\"" % (";".join(filter_chains)),
            "-filter_complex_script \"%s\"" % (temp_filter_script),
            # define duration
            # if video should be loopable, skip the start fade-in (-ss) and the end fade-out (video is stopped after the fade-in of the last image which is the same as the first-image)
            "-ss %s -t %s" %(self.getSlides()[0].fade_duration, self.getOffset(-1)) if self.config["loopable"] else "-t %s" %(self.getTotalDuration()),
            # define output
            "-map", "[out]:v",
            "-c:v", "libx264", 
            #"-crf", "0" ,
            "-preset", "ultrafast", 
            "-tune", "stillimage",
            "-map [aout]:a" if self.hasAudio() else "",
            # audio compression and bitrate
            "-c:a aac" if self.hasAudio() else "",
            "-b:a 160k" if self.hasAudio() else "",
            # map subtitles (only mkv)
            "-map %s:s" %(srtInput) if self.hasSubtitles() and not burnSubtitles else "",
            # set subtitles enabled (only mkv)
            "-disposition:s:s:0 default" if self.hasSubtitles() and not burnSubtitles else "",
            output_file
        ]  

        logger.info("FFMPEG started")
        subprocess.call(" ".join(cmd))
        logger.info("FFMPEG finished")
        
        if self.config["delete_temp"]:
            logger.info("Delete temporary files")
            for temp in self.tempfiles:
                os.remove(temp)
                logger.debug("Delete %s", temp)

        os.remove(temp_filter_script)
        os.remove(srtFilename)
                
    def saveConfig(self, filename):
        logger.info("Save config to %s", filename)
        
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
            
    def createSubtitles(self, filename):
        with open('%s' %(filename), 'w') as file:
            subtitle_index = 1
            for i, slide in enumerate(self.slides):
                if slide.title is not None:
                    offset = self.getOffset(i)
                    st = datetime.timedelta(seconds=offset)
                    srt_start = '%02d:%02d:%02d,%03d' % (st.seconds//3600, (st.seconds//60)%60, st.seconds, st.microseconds / 1000)
                    st = datetime.timedelta(seconds=offset + slide.duration)
                    srt_end = '%02d:%02d:%02d,%03d' % (st.seconds//3600, (st.seconds//60)%60, st.seconds, st.microseconds / 1000)

                    file.write("%s\n" %(subtitle_index))
                    file.write("%s --> %s\n" %(srt_start, srt_end))
                    file.write("%s\n\n" % (slide.title))
                    subtitle_index += 1