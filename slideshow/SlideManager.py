import subprocess
import os
import json
import sys
import logging
import datetime
import re
import importlib

from .Slide import Slide
from .ImageSlide import ImageSlide
from .VideoSlide import VideoSlide
from .AudioFile import AudioFile
from .Queue import Queue

logger = logging.getLogger("kburns-slideshow")

class SlideManager:

    def __init__(self, config, input_files, audio_files):
        self.slides = []
        self.background_tracks = []
        self.config = config

        self.tempFilePrefix = "temp-kburns-"
        self.queue = Queue(self.tempFilePrefix)
        
        self.tempInputFiles = []
        
        self.reduceVariable = 10
        
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
                    
                transition = self.config["transition"]
                if isinstance(file, dict) and "transition" in file:
                    transition = file["transition"]
                    
                extension = filename.split(".")[-1]
                
                if extension.lower() in [e.lower() for e in self.config["VIDEO_EXTENSIONS"]]:
                    slide = VideoSlide(filename, self.config["ffprobe"], output_width, output_height, fade_duration, title, fps, overlay_text, transition)
                if extension.lower() in [e.lower() for e in self.config["IMAGE_EXTENSIONS"]]:
                    slide = ImageSlide(filename, output_width, output_height, slide_duration, slide_duration_min, fade_duration, zoom_direction, scale_mode, zoom_rate, fps, title, overlay_text, transition)
            
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
        last_slide = self.getSlides()[-1]
        last_slide_start = self.getOffset(-1)
        
        return (last_slide_start + last_slide.getFrames())/self.config["fps"]
    
    def getVideoAudioDuration(self):
        return sum([slide.getDuration() for slide in self.getVideos() if slide.has_audio])
    
    def getAudioDuration(self):
        return sum([audio.duration for audio in self.getBackgroundTracks()])
            
    # next slide starts on 
    # previous slides start 
    # + slides duration 
    # - fade-out duration (begin of transition) 
    def getOffset(self, idx, frames = True):
        offset = sum([slide.getFrames() - self.getSlideFadeOutDuration(i) for i, slide in enumerate(self.getSlides()[:idx])])
        return offset if frames else round(offset/self.config["fps"], 5)
        
    def getMusicFadeOutDuration(self, idx):
        # first and last slide should fade the total music in/out
        if idx < 0 or idx == len(self.getSlides())-1:
            slide = self.getSlides()[idx]
            return slide.getDuration()
        return self.getSlideFadeOutDuration(idx, False)
    
    def getSlideFadeOutDuration(self, idx, frames = True):
        # first slide has no previous slide
        if idx < 0:
            return 0
        
        # last slide has no fade-out
        if idx == len(self.getSlides())-1:
            return 0
        
        # is the next slide long enough to have a fade-in and a fade-out?
        if idx + 1 < len(self.getSlides()):
            if not self.isSlideDurationGreaterThanFadeDuration(idx+1, 2):
                return 0
        
        # is current slide long enough to have a fade-in and fade-out?
        if self.isSlideDurationGreaterThanFadeDuration(idx, 2):
            slide = self.getSlides()[idx]
            return slide.fade_duration*self.config["fps"] if frames else slide.fade_duration
        
        return 0
    
    def isSlideDurationGreaterThanFadeDuration(self,idx, multiplier = 2):
        # duration of current slide needs to be longer than 
        # the duration of the fade-in + the duration of the fade-out
        # first slide has only fade-in
        # last slide has only fade-out
        if idx == 0 or idx == len(self.getSlides())-1:
            multiplier = 1
            
        slide = self.getSlides()[idx]
        # is the duration of the slide long enough to have a fade-in and fade-out
        if slide.getDuration() >= slide.fade_duration*multiplier:
            return True
        
        return False
        
    def getSlideFadeOutPosition(self, idx, frames = True):
        slide = self.getSlides()[idx]
        pos_frames = slide.getFrames() - self.getSlideFadeOutDuration(idx)
        return pos_frames if frames else round(pos_frames/self.config["fps"], 3)
        
    def getSlideTransition(self, idx):
        slide = self.getSlides()[idx]
        return slide.transition
        
    def getVideoFilterChains(self, burnSubtitles = False, srtFilename = ""):
    
        logger.debug("get Video Filter Chains")
        
        # Base black image
        filter_chains = []
        
        for i, slide in enumerate(self.getSlides()):
        
            filters = slide.getFilter()
            
            # generate temporary video of zoom/pan effect
            if self.config["generate_temp"] and isinstance(slide, ImageSlide):
                # fix scaling
                filters.append("setsar=1")
                
                slide.tempfile = self.queue.addItem([slide.file], filters, i)

                filters = []

            
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
            filters.append("setpts=PTS-STARTPTS")
            
            # while scaling the SAR is changed as well, so we need to reset it here:
            # see https://trac.ffmpeg.org/ticket/1079#comment:2
            # see https://ffmpeg.org/ffmpeg-filters.html#scale-1 
            # The scale filter forces the output display aspect ratio to be the same 
            # of the input, by changing the output sample aspect ratio. 
            filters.append("setsar=1")
            
            # add transparency for possible fade-in/fade-out
            filters.append("format=rgba")
            
            # split video in start, main, end sections
            
            # get fade in duration from previous slides fade duration
            fade_in_end = self.getSlideFadeOutDuration(i-1, True) if i > 0 else 0
            fade_out_start = self.getSlideFadeOutPosition(i, True)
            
            splits = []
            if fade_in_end > 0:
                splits.append("start")
            if fade_out_start < slide.getFrames():
                splits.append("end")
            if fade_out_start > fade_in_end:
                splits.append("main")
                
            slide.splits = splits
            
            if self.config["generate_temp"]:
                for step in splits:
                    tempfilters = filters[:]
                    
                    if step == "start":
                        tempfilters.append("trim=start_frame=%s:end_frame=%s,setpts=PTS-STARTPTS" %(0, fade_in_end))
                        
                    if step == "main":
                        tempfilters.append("trim=start_frame=%s:end_frame=%s,setpts=PTS-STARTPTS" %(fade_in_end, fade_out_start))
                        
                    if step == "end":
                        tempfilters.append("trim=start_frame=%s:end_frame=%s,setpts=PTS-STARTPTS" %(fade_out_start, slide.getFrames()))
                        
                    file = slide.tempfile if isinstance(slide, ImageSlide) else slide.file
                    self.queue.addItem([file], tempfilters, "%s_%s" %(i, step))
            else:
                filters.append("split=%s" %(len(splits)))
                filter_chains.append("[%s:v]" %(i) + ", ".join(filters) + "".join(["[v%sout-%s]" %(i, s) for s in splits])) 

                # prevent buffer overflow with fifo:
                # https://trac.ffmpeg.org/ticket/4950#comment:1 
                # https://superuser.com/a/1135202
                # https://superuser.com/a/1148850
                # https://stackoverflow.com/a/40746988
                # https://stackoverflow.com/a/51978577
                if "start" in splits:
                    filter_chains.append("[v%sout-start]fifo,trim=start_frame=%s:end_frame=%s,setpts=PTS-STARTPTS[v%sstart]" %(i, 0, fade_in_end, i))
                if "main" in splits:
                    filter_chains.append("[v%sout-main]fifo,trim=start_frame=%s:end_frame=%s,setpts=PTS-STARTPTS[v%smain]" %(i, fade_in_end, fade_out_start, i))
                if "end" in splits:
                    filter_chains.append("[v%sout-end]fifo,trim=start_frame=%s:end_frame=%s,setpts=PTS-STARTPTS[v%send]" %(i, fade_out_start, slide.getFrames(), i))
                
                
        subtitles = ""
        # Burn subtitles to last element
        if burnSubtitles and self.hasSubtitles():
            subtitles = ",subtitles=%s" %(srtFilename)
            
        # Concat videos
        videos = []
        for i, slide in enumerate(self.getSlides()):
            if "start" in slide.splits:
                if self.config["generate_temp"]:
                    end         = "[v0]"
                    start       = "[v1]"
                    transition  = ""
                else:
                    end         = "[v%send]" %(i-1)
                    start       = "[v%sstart]" %(i)
                    transition  = "[v%strans]" % (i)
                    
                filter = self.getTransition(i-1, end, start, transition)
                
                if filter is not None:
                    if self.config["generate_temp"]:
                        # temporary transition video
                        tempvideo_end = "%s%s_%s.mp4" %(self.tempFilePrefix, i-1, "end")
                        tempvideo_start = "%s%s_%s.mp4" %(self.tempFilePrefix, i, "start")
                        
                        filter = "[0:v]format=rgba[v0];[1:v]format=rgba[v1];%s, setsar=1" %(filter)
                        
                        trans_slide = self.getSlides()[i-1]
                        output = self.queue.addItem([tempvideo_end, tempvideo_start], filter, "%s_trans_%s" %(i, trans_slide.transition))
                        
                        self.tempInputFiles.append(output)
                    else:
                        filter_chains.append(filter)
                        videos.append(transition)
                else:
                    if self.config["generate_temp"]:
                        self.tempInputFiles.append("temp-kburns-%s_%s.mp4" %(i-1, "end"))
                        self.tempInputFiles.append("temp-kburns-%s_%s.mp4" %(i, "start"))
                    else:
                        videos.append("[v%send]" %(i-1))
                        videos.append("[v%sstart]" %(i))

            # append video between transitions
            if "main" in slide.splits:
                if self.config["generate_temp"]:
                    self.tempInputFiles.append("temp-kburns-%s_%s.mp4" %(i, "main"))
                else:
                    videos.append("[v%smain]" %(i))
            
            # on the last slide the end needs to be added (if available)
            #if "end" in slide.splits and i == len(self.getSlides())-1:
            #    videos.append("[v%send]" %(i))
        
        # use input files instead of filter outputs
        if self.config["generate_temp"]:
            count = 0
            while len(self.tempInputFiles) > self.reduceVariable:
                files = self.tempInputFiles
                self.tempInputFiles = []
                temp = []
                for k, video in enumerate(files):
                    temp.append(video)
                    if len(temp) >= self.reduceVariable:
                        filter_names = ["[%s]" %(i) for i in range(len(temp))]
                        filter = "%s concat=n=%s" %("".join(filter_names), len(filter_names))
                        
                        output = self.queue.addItem(temp, filter, "%s_%s_combine" %(count, k))
                        
                        # add concated video
                        self.tempInputFiles.append(output)
                        
                        temp = []
                
                # add remaining files
                self.tempInputFiles.extend(temp)
                count = count + 1
            
            videos = ["[%s:v]" %(i) for i in range(len(self.tempInputFiles))]
        
        filter_chains.append("%s concat=n=%s:v=1:a=0%s,format=yuv420p[out]" %("".join(videos), len(videos), subtitles))
            
        return filter_chains
        
    def getBackgroundTracks(self):
        return self.background_tracks
        
    def hasAudio(self):
        return len(self.background_tracks)> 0 or len([video for video in self.getVideos() if video.has_audio]) > 0
        
    def hasSubtitles(self):
        return len([slide for slide in self.getSlides() if slide.title is not None]) > 0        
        
    def getAudioFilterChains(self):
    
        logger.debug("get Audio Filter Chains")
        
        offset = len(self.tempInputFiles)
        
        filter_chains = []

        # audio from video slides
        audio_tracks = []
        for i, slide in enumerate(self.getSlides()):
            if isinstance(slide, VideoSlide) and slide.has_audio:
                audio_tracks.append("[a%s]" %(i))
                
                filters = []
                # Fade music in filter
                if slide.fade_duration > 0:
                    filters.append("afade=t=in:st=0:d=%s" %(self.getSlideFadeOutDuration(i-1, False)))
                    filters.append("afade=t=out:st=%s:d=%s" %(self.getSlideFadeOutPosition(i, False), self.getSlideFadeOutDuration(i, False) ))
                filters.append("adelay=%s|%s" %( int(self.getOffset(i, False)*1000), int(self.getOffset(i, False)*1000)))
                
                input_number = i
                # append video with sound to input list
                if self.config["generate_temp"]:
                    input_number = offset
                    self.tempInputFiles.append(slide.file)
                    offset = offset + 1
                
                filter_chains.append("[%s:a] %s [a%s]" %(input_number, ",".join(filters), i))
        
        # background-tracks
        music_input_offset = len(self.getSlides()) if not self.config["generate_temp"] else len(self.tempInputFiles)
        background_audio = ["[%s:a]" %(i+music_input_offset) for i, track in enumerate(self.background_tracks)]
        
        if len(background_audio) > 0:
            # extract background audio sections between videos
            background_sections = []
            # is it starting with a video or an image?
            section_start_slide = None if isinstance(self.getSlides()[0], VideoSlide) else 0
            for i, slide in enumerate(self.getSlides()):
                # is it a video and we have a start value => end of this section
                if isinstance(slide, VideoSlide) and slide.has_audio and section_start_slide is not None:
                    background_sections.append({ "start": self.getOffset(section_start_slide, False), "fade_in": self.getMusicFadeOutDuration(section_start_slide-1), "end": self.getOffset(i, False), "fade_out": self.getMusicFadeOutDuration(i) })
                    section_start_slide = None
                
                # is it a image but the previous one was a video => start new section
                if isinstance(slide, ImageSlide) and section_start_slide is None:
                    section_start_slide = i

            # the last section is ending with an image => end of section is end generated video
            if section_start_slide is not None:
                background_sections.append({ "start": self.getOffset(section_start_slide, False), "fade_in": self.getMusicFadeOutDuration(section_start_slide-1), "end": self.getTotalDuration() - self.getMusicFadeOutDuration(i), "fade_out": self.getMusicFadeOutDuration(i) })
                
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
        
    def getTimestampsFromAudio(self):
        
        logger.debug("get Timestamps from Audio Files")
        
        timestamps = []
        offset = 0
        for track in self.getBackgroundTracks():
            # add beginning of track
            timestamps.append(0+offset)
            # get timestamps of track
            timestamps = timestamps + [float(timestamp)+offset for timestamp in track.getTimestamps(self.config["aubio"])]
            # next track has the offsets after the current
            offset = offset + track.duration
        
        logger.debug("Timestamps: %s", timestamps)

        return timestamps
        
    def adjustDurationsFromAudio(self):
        
        logger.debug("adjust slide durations")
        
        timestamps = self.getTimestampsFromAudio()
        
        logger.debug("Slide durations (before): %s", [slide.getDuration() for slide in self.getSlides()])
        
        # change slide durations
        timestamp_idx = 0
        for i, slide in enumerate(self.getSlides()):
            if not slide.has_audio and not isinstance(slide, VideoSlide) and timestamp_idx < len(timestamps):
                
                slide_start = self.getOffset(i, False)
                
                # find the next timestamp after the slide starts 
                # and skip timestamps until the minimum duration is reached
                no_result = False
                while (slide_start >= (timestamps[timestamp_idx]) or (timestamps[timestamp_idx] - slide_start) < slide.slide_duration_min):
                    # is the music long enough?
                    if (timestamp_idx+1)  < len(timestamps):
                        timestamp_idx = timestamp_idx + 1
                    else:
                        no_result = True
                        break

                if not no_result:
                    duration = timestamps[timestamp_idx] - slide_start

                    # the next timestamp is earlier than the initial slide duration and after the minimum? => set the new duration
                    if duration < slide.getDuration():
                        # extend slide duration for a half fade so that the middle of the transition matches the timestamp
                        # timestamp matches fade end:    duration
                        # timestamp matches fade middle: duration + self.getSlideFadeOutDuration(i)/2
                        # timestamp matches fade begin:  duration + self.getSlideFadeOutDuration(i)
                        slide.setDuration(duration + self.getSlideFadeOutDuration(i)/2/self.config["fps"])
                        timestamp_idx = timestamp_idx + 1

        logger.debug("Slide durations (after): %s", [slide.getDuration() for slide in self.getSlides()])
            
    def getTransition(self, i, end  = "", start = "", transition = ""):
        fade_duration = self.getSlideFadeOutDuration(i, False)
        # blend between previous slide and this slide
        if fade_duration > 0:
            # Load effect
            try:
                effect = importlib.import_module('slideshow.effects.%s' %(self.getSlideTransition(i)))
                filter = effect.get(end, start, transition, i, fade_duration, self.config)
                return filter
            except ModuleNotFoundError:
                return None
        
        # fade duration is too long for slides duration
        return None
            
    def createVideo(self, output_file):
        logger.info("Create video %s", output_file)
        
        # check if it is okay to have a shorter background track
        video_duration = self.getTotalDuration()
        audio_duration = self.getAudioDuration() + self.getVideoAudioDuration()
        logger.info("Video length: %s", video_duration)
        logger.info("Background track length: %s", audio_duration)
        if len(self.background_tracks)> 0 and audio_duration < video_duration:
            print("Background track (%s) is shorter than video length (%s)!" %(audio_duration, video_duration))
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
        video_filters = self.getVideoFilterChains(burnSubtitles, srtFilename)
        
        # Get Input Files
        inputs = [slide.file for slide in self.getSlides()]
        if self.config["generate_temp"]:
            inputs = self.tempInputFiles
        
        # Get Audio Filter
        audio_filters = self.getAudioFilterChains()
        
        temp_filter_script = "temp-kburns-video-script.txt"
        with open('%s' %(temp_filter_script), 'w') as file:
            file.write(";\n".join(video_filters + audio_filters))
            
        # Get Frames
        frames = round(sum([slide.getFrames() for slide in self.getSlides()]))
        print("Number of Frames: %s" %(frames))
        logger.info("Number of Frames: %s",frames)

        # create temporary videos
        self.queue.createTemporaryVideos(self.config["ffmpeg"])
        
        # Run ffmpeg
        cmd = [ self.config["ffmpeg"], 
            "-hide_banner", 
            #"-v quiet",
            "-stats",
            "-y" if self.config["overwrite"] else "",
            # slides
            " ".join(["-i \"%s\" " %(f) for f in inputs]),
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
        logger.debug(" ".join(cmd))
        subprocess.call(" ".join(cmd))
        logger.info("FFMPEG finished")
        
        if self.config["delete_temp"]:
            logger.info("Delete temporary files")
            self.queue.clean()

        if os.path.exists(temp_filter_script):
            os.remove(temp_filter_script)
        if os.path.exists(srtFilename):
            os.remove(srtFilename)
                
    def saveConfig(self, filename):
        logger.info("Save config to %s", filename)
        
        content = {
            "config": {
                "output_width": self.config["output_width"],
                "output_height": self.config["output_height"],
                "slide_duration": self.config["slide_duration"],
                "slide_duration_min": self.config["slide_duration_min"],
                "fade_duration": self.config["fade_duration"],
                "transition": self.config["transition"],
                "transition_bars_count": self.config["transition_bars_count"],
                "transition_cell_size": self.config["transition_cell_size"],
                "fps": self.config["fps"],
                "zoom_rate": self.config["zoom_rate"],
                "zoom_direction": self.config["zoom_direction"],
                "scale_mode": self.config["scale_mode"],
                "loopable": self.config["loopable"],
                "overwrite": self.config["overwrite"],
                "generate_temp": self.config["generate_temp"],
                "delete_temp": self.config["delete_temp"]
            }, 
            "slides": [slide.getObject(self.config) for slide in self.slides],
            "audio":  [track.getObject() for track in self.getBackgroundTracks()]
        }
        with open('%s' %(filename), 'w') as file:
            json.dump(content, file, indent=4)
            
    def createSubtitles(self, filename):
        with open('%s' %(filename), 'w') as file:
            subtitle_index = 1
            for i, slide in enumerate(self.slides):
                if slide.title is not None:
                    # start the subtitle when the fade-in is done
                    offset = self.getOffset(i, False) + self.getSlideFadeOutDuration(i-1, False)
                    srt_start = self.getSubtitleFormat(offset)
                    
                    # end the subtitle when the fade-out is done
                    offset_next = self.getOffset(i+1, False) + self.getSlideFadeOutDuration(i, False)
                    srt_end = self.getSubtitleFormat(offset_next)

                    file.write("%s\n" %(subtitle_index))
                    file.write("%s --> %s\n" %(srt_start, srt_end))
                    file.write("%s\n\n" % (slide.title))
                    subtitle_index += 1
                    
    def getSubtitleFormat(self, seconds):
        millis = seconds * 1000
        milliseconds = millis%1000
        seconds= int((millis/1000)%60)
        minutes=int((millis/(1000*60))%60)
        hours=(millis/(1000*60*60))%24
        
        return '%02d:%02d:%02d,%03d' % (hours, minutes, seconds, milliseconds)