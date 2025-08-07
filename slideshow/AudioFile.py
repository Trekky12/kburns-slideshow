#!/usr/bin/env python3

import subprocess


class AudioFile:

    def __init__(self, file, ffprobe, audio_start=None, audio_end=None):

        self.file = file

        duration = subprocess.check_output(["%s" % (ffprobe), "-show_entries", "format=duration",
                                            "-v", "error", "-of", "default=noprint_wrappers=1:nokey=1", file]).decode()
        self.duration = 0
        self.audio_duration = float(duration)

        self.is_trimmed = False
        self.start = audio_start if audio_start is not None else None
        self.end = audio_end if audio_end is not None and audio_end < self.audio_duration else None
        self.calculateDurationAfterTrimming()

    def calculateDurationAfterTrimming(self):
        if self.start is not None or self.end is not None:
            self.is_trimmed = True

            # calculate new duration
            start = self.start if self.start is not None else 0
            end = self.end if self.end is not None else self.audio_duration
            duration = end - start

            self.duration = duration
        else:
            self.is_trimmed = False
            self.duration = self.audio_duration

    def getAudioFilter(self):
        if self.is_trimmed:
            trim = []
            if self.start is not None:
                trim.append("start=%s" % (self.start))
            if self.end is not None:
                trim.append("end=%s" % (self.end))

            return "atrim=%s,asetpts=PTS-STARTPTS" % (":".join(trim))

        return "anull"

    def getTimestamps(self, aubio):
        timestamps = subprocess.check_output(["%s" % (aubio), "-i", self.file, "-O", "kl"],
                                             stderr=subprocess.DEVNULL).decode().splitlines()

        # Convert timestamps to float
        timestamps = [float(timestamp) for timestamp in timestamps]

        # Apply trimming
        if self.end is not None:
            timestamps = [timestamp for timestamp in timestamps if timestamp < self.end]
        if self.start is not None:
            timestamps = [timestamp - self.start for timestamp in timestamps if timestamp >= self.start]

        return [0.0] + timestamps

    def getObject(self):
        object = {"file": self.file}

        if self.start is not None:
            object["start"] = self.start

        if self.end is not None:
            object["end"] = self.end

        return object
