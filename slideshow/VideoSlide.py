#!/usr/bin/env python3

from .Slide import Slide
import subprocess


class VideoSlide(Slide):

    def __init__(self, ffmpeg_version, file, ffprobe, output_width, output_height,
                 fade_duration=1, title=None, fps=60, overlay_text=None, overlay_color=None,
                 transition="random", pad_color="black", blurred_padding=False,
                 force_no_audio=False, video_start=None, video_end=None):
        duration = self.subprocess_call(["%s" % (ffprobe), "-show_entries", "format=duration",
                                         "-v", "error", "-of", "default=noprint_wrappers=1:nokey=1", file])
        duration = float(duration)

        self.video_duration = duration

        super().__init__(ffmpeg_version, file, output_width, output_height,
                         duration, fade_duration, fps, title, overlay_text, overlay_color,
                         transition, pad_color, blurred_padding)

        audio = self.subprocess_call(["%s" % (ffprobe), "-select_streams", "a", "-show_entries",
                                      "stream=codec_type", "-v", "error", "-of", "default=noprint_wrappers=1:nokey=1", file])
        self.video_has_audio = "audio" in str(audio)
        self.has_audio = self.video_has_audio

        width = self.subprocess_call(["%s" % (ffprobe), "-select_streams", "v", "-show_entries",
                                      "stream=width", "-v", "error", "-of", "default=noprint_wrappers=1:nokey=1", file])
        self.width = int(width)

        height = self.subprocess_call(["%s" % (ffprobe), "-select_streams", "v", "-show_entries",
                                       "stream=height", "-v", "error", "-of", "default=noprint_wrappers=1:nokey=1", file])
        self.height = int(height)

        self.ratio = self.width / self.height

        self.setForceNoAudio(force_no_audio)

        self.is_trimmed = False
        self.start = video_start if video_start is not None else None
        self.end = video_end if video_end is not None and video_end < self.duration else None
        self.calculateDurationAfterTrimming()

    def calculateDurationAfterTrimming(self):
        if self.start is not None or self.end is not None:
            self.is_trimmed = True

            # calculate new duration
            start = self.start if self.start is not None else 0
            end = self.end if self.end is not None else self.duration
            duration = end - start

            self.setDuration(duration)
        else:
            self.is_trimmed = False

    def setForceNoAudio(self, force_no_audio):
        self.force_no_audio = force_no_audio
        if force_no_audio:
            self.has_audio = False
        else:
            self.has_audio = self.video_has_audio

    def getFilter(self, index):
        width, height = [self.output_width, -1]
        if self.ratio <= self.output_ratio:
            width, height = [-1, self.output_height]

        video_filters = []
        video_filters.append("scale=w=%s:h=%s" % (width, height))
        video_filters.append("fps=%s" % (self.fps))
        video_filters.append("pad=%s:%s:'(ow-iw)/2':'(oh-ih)/2':color=%s" % (self.output_width, self.output_height, self.pad_color))

        if self.is_trimmed:
            trim = []
            if self.start is not None:
                trim.append("start=%s" % (self.start))
            if self.end is not None:
                trim.append("end=%s" % (self.end))

            video_filters.append("trim=%s,setpts=PTS-STARTPTS" % (":".join(trim)))

        return video_filters

    def getAudioFilter(self):
        if self.is_trimmed:
            trim = []
            if self.start is not None:
                trim.append("start=%s" % (self.start))
            if self.end is not None:
                trim.append("end=%s" % (self.end))

            return "atrim=%s,asetpts=PTS-STARTPTS" % (":".join(trim))

        return None

    def getObject(self, config):
        object = super().getObject(config)

        object["force_no_audio"] = self.force_no_audio

        if self.start is not None:
            object["start"] = self.start

        if self.end is not None:
            object["end"] = self.end

        return object

    def subprocess_call(self, command=[]):
        si = None
        if hasattr(subprocess, 'STARTUPINFO'):
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        return subprocess.check_output(command, stderr=subprocess.PIPE, stdin=subprocess.PIPE, startupinfo=si).decode()
