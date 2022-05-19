import tkinter as tk
from tkinter import ttk

import json

import logging

from .ScrollFrame import ScrollFrame

logger = logging.getLogger("kburns-slideshow")


class ConfigFrame(tk.Toplevel):
    def __init__(self, parent, **options):
        super().__init__()

        self.inputffmpeg = tk.StringVar()
        self.inputffprobe = tk.StringVar()
        self.inputAubio = tk.StringVar()

        self.inputLoopable = tk.BooleanVar()
        self.inputOverwrite = tk.BooleanVar()
        self.inputGenerateTemp = tk.BooleanVar()
        self.inputDeleteTemp = tk.BooleanVar()
        self.inputSyncToAudio = tk.BooleanVar()

        self.inputOutputWidth = tk.StringVar()
        self.inputOutputHeight = tk.StringVar()
        self.inputOutputParameters = tk.StringVar()
        self.inputOutputCodec = tk.StringVar()
        self.inputFPS = tk.StringVar()
        self.inputDuration = tk.StringVar()
        self.inputDurationMin = tk.StringVar()
        self.inputZoomRate = tk.StringVar()
        self.inputZoomDirectionX = tk.StringVar()
        self.inputZoomDirectionY = tk.StringVar()
        self.inputZoomDirectionZ = tk.StringVar()
        self.inputScaleMode = tk.StringVar()
        self.inputPadColor = tk.StringVar()

        self.inputTransitionDuration = tk.StringVar()
        self.inputTransition = tk.StringVar()
        self.inputTransitionBars = tk.StringVar()
        self.inputTransitionCells = tk.StringVar()

        self.inputTempFileFolder = tk.StringVar()
        self.inputTempFilePrefix = tk.StringVar()

        self.config = {}
        self.config_path = None

    def create(self, config_path, choices):

        self.config_path = config_path

        with open(self.config_path) as config_file:
            self.config = json.load(config_file)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.geometry("700x700")

        scrollFrame = ScrollFrame(self, 200, True)
        scrollFrame.grid(row=0, column=0, sticky=tk.NSEW)

        configFrame = tk.Frame(scrollFrame.getCanvas())

        pathFrame = tk.LabelFrame(configFrame, text="Paths")
        pathFrame.grid(row=0, column=0, sticky=tk.NSEW, padx=4, pady=4)

        self.inputffmpeg.set(self.config["ffmpeg"])
        ffmpegLabel = tk.Label(pathFrame, text="FFmpeg")
        ffmpegLabel.grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        ffmpegEntry = tk.Entry(pathFrame, width=70, textvariable=self.inputffmpeg)
        ffmpegEntry.grid(row=0, column=1, columnspan=3, sticky=tk.W, padx=4, pady=4)

        self.inputffprobe.set(self.config["ffprobe"])
        ffprobeLabel = tk.Label(pathFrame, text="FFprobe")
        ffprobeLabel.grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
        ffprobeEntry = tk.Entry(pathFrame, width=70, textvariable=self.inputffprobe)
        ffprobeEntry.grid(row=1, column=1, columnspan=3, sticky=tk.W, padx=4, pady=4)

        self.inputAubio.set(self.config["aubio"])
        aubioLabel = tk.Label(pathFrame, text="aubio")
        aubioLabel.grid(row=2, column=0, sticky=tk.W, padx=4, pady=4)
        aubioEntry = tk.Entry(pathFrame, width=70, textvariable=self.inputAubio)
        aubioEntry.grid(row=2, column=1, columnspan=3, sticky=tk.W, padx=4, pady=4)

        outputFrame = tk.LabelFrame(configFrame, text="Output")
        outputFrame.grid(row=1, column=0, sticky=tk.NSEW, padx=4, pady=4)

        self.inputOutputWidth.set(self.config["output_width"])
        widthLabel = tk.Label(outputFrame, text="Width")
        widthLabel.grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        widthEntry = tk.Entry(outputFrame, textvariable=self.inputOutputWidth)
        widthEntry.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputOutputHeight.set(self.config["output_height"])
        heightLabel = tk.Label(outputFrame, text="Height")
        heightLabel.grid(row=0, column=2, sticky=tk.W, padx=4, pady=4)
        heightEntry = tk.Entry(outputFrame, textvariable=self.inputOutputHeight)
        heightEntry.grid(row=0, column=3, sticky=tk.W, padx=4, pady=4)

        self.inputOutputParameters.set(self.config["output_parameters"])
        parametersLabel = tk.Label(outputFrame, text="Parameters")
        parametersLabel.grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
        parametersEntry = tk.Entry(outputFrame, width=67, textvariable=self.inputOutputParameters)
        parametersEntry.grid(row=1, column=1, columnspan=3, sticky=tk.W, padx=4, pady=4)

        self.inputOutputCodec.set(self.config["output_codec"])
        codecLabel = tk.Label(outputFrame, text="Codec")
        codecLabel.grid(row=2, column=0, sticky=tk.W, padx=4, pady=4)
        codecEntry = tk.Entry(outputFrame, textvariable=self.inputOutputCodec)
        codecEntry.grid(row=2, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputFPS.set(self.config["fps"])
        fpsLabel = tk.Label(outputFrame, text="FPS")
        fpsLabel.grid(row=3, column=0, sticky=tk.W, padx=4, pady=4)
        fpsEntry = tk.Entry(outputFrame, textvariable=self.inputFPS)
        fpsEntry.grid(row=3, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputLoopable.set(self.config["loopable"])
        loopableLabel = tk.Label(outputFrame, text="Loopable")
        loopableLabel.grid(row=4, column=0, sticky=tk.W, padx=4, pady=4)
        loopableCheckBox = tk.Checkbutton(outputFrame, var=self.inputLoopable)
        loopableCheckBox.grid(row=4, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputOverwrite.set(self.config["overwrite"])
        overwriteLabel = tk.Label(outputFrame, text="Overwrite")
        overwriteLabel.grid(row=5, column=0, sticky=tk.W, padx=4, pady=4)
        overwriteCheckBox = tk.Checkbutton(outputFrame, var=self.inputOverwrite)
        overwriteCheckBox.grid(row=5, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputSyncToAudio.set(self.config["sync_to_audio"])
        syncToAudioLabel = tk.Label(outputFrame, text="Sync to Audio")
        syncToAudioLabel.grid(row=6, column=0, sticky=tk.W, padx=4, pady=4)
        syncToAudioCheckBox = tk.Checkbutton(outputFrame, var=self.inputSyncToAudio)
        syncToAudioCheckBox.grid(row=6, column=1, sticky=tk.W, padx=4, pady=4)

        tempFrame = tk.LabelFrame(configFrame, text="Temporary files")
        tempFrame.grid(row=2, column=0, sticky=tk.NSEW, padx=4, pady=4)

        self.inputTempFileFolder.set(self.config["temp_file_folder"])
        tempFileFolderLabel = tk.Label(tempFrame, text="Folder")
        tempFileFolderLabel.grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        tempFileFolderEntry = tk.Entry(tempFrame, textvariable=self.inputTempFileFolder)
        tempFileFolderEntry.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputTempFilePrefix.set(self.config["temp_file_prefix"])
        tempFilePrefixLabel = tk.Label(tempFrame, text="Prefix")
        tempFilePrefixLabel.grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
        tempFilePrefixEntry = tk.Entry(tempFrame, textvariable=self.inputTempFilePrefix)
        tempFilePrefixEntry.grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputGenerateTemp.set(self.config["generate_temp"])
        generateTempLabel = tk.Label(tempFrame, text="Generate")
        generateTempLabel.grid(row=2, column=0, sticky=tk.W, padx=4, pady=4)
        generateTempCheckBox = tk.Checkbutton(tempFrame, var=self.inputGenerateTemp)
        generateTempCheckBox.grid(row=2, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputDeleteTemp.set(self.config["delete_temp"])
        deleteTempLabel = tk.Label(tempFrame, text="Delete")
        deleteTempLabel.grid(row=2, column=2, sticky=tk.W, padx=4, pady=4)
        deleteTempCheckBox = tk.Checkbutton(tempFrame, var=self.inputDeleteTemp)
        deleteTempCheckBox.grid(row=2, column=3, sticky=tk.W, padx=4, pady=4)

        slideFrame = tk.LabelFrame(configFrame, text="Image Slides")
        slideFrame.grid(row=3, column=0, sticky=tk.NSEW, padx=4, pady=4)

        self.inputDuration.set(self.config["slide_duration"])
        durationLabel = tk.Label(slideFrame, text="Duration")
        durationLabel.grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        durationEntry = tk.Entry(slideFrame, textvariable=self.inputDuration)
        durationEntry.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputDurationMin.set(self.config["slide_duration_min"])
        durationMinLabel = tk.Label(slideFrame, text="Duration (min)")
        durationMinLabel.grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
        durationMinEntry = tk.Entry(slideFrame, textvariable=self.inputDurationMin)
        durationMinEntry.grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputZoomRate.set(self.config["zoom_rate"])
        zoomRateLabel = tk.Label(slideFrame, text="Zoom Rate")
        zoomRateLabel.grid(row=2, column=0, sticky=tk.W, padx=4, pady=4)
        zoomRateEntry = tk.Entry(slideFrame, textvariable=self.inputZoomRate)
        zoomRateEntry.grid(row=2, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputZoomDirectionX.set(self.config["zoom_direction_x"])
        zoomDirectionXLabel = tk.Label(slideFrame, text="Zoom Direction X")
        zoomDirectionXLabel.grid(row=3, column=0, sticky=tk.W, padx=4, pady=4)
        zoomDirectionXCombo = ttk.Combobox(slideFrame, values=choices["zoom_direction_x"],
                                           textvariable=self.inputZoomDirectionX)
        zoomDirectionXCombo.grid(row=3, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputZoomDirectionY.set(self.config["zoom_direction_y"])
        zoomDirectionYLabel = tk.Label(slideFrame, text="Zoom Direction Y")
        zoomDirectionYLabel.grid(row=4, column=0, sticky=tk.W, padx=4, pady=4)
        zoomDirectionYCombo = ttk.Combobox(slideFrame, values=choices["zoom_direction_y"],
                                           textvariable=self.inputZoomDirectionY)
        zoomDirectionYCombo.grid(row=4, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputZoomDirectionZ.set(self.config["zoom_direction_z"])
        zoomDirectionZLabel = tk.Label(slideFrame, text="Zoom Direction Z")
        zoomDirectionZLabel.grid(row=5, column=0, sticky=tk.W, padx=4, pady=4)
        zoomDirectionZCombo = ttk.Combobox(slideFrame, values=choices["zoom_direction_z"],
                                           textvariable=self.inputZoomDirectionZ)
        zoomDirectionZCombo.grid(row=5, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputScaleMode.set(self.config["scale_mode"])
        scaleModeLabel = tk.Label(slideFrame, text="Scale Mode")
        scaleModeLabel.grid(row=6, column=0, sticky=tk.W, padx=4, pady=4)
        scaleModeCombo = ttk.Combobox(slideFrame, values=choices["scale_mode"], textvariable=self.inputScaleMode)
        scaleModeCombo.grid(row=6, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputPadColor.set(self.config["pad_color"] if "pad_color" in self.config else "black")
        padColorLabel = tk.Label(slideFrame, text="Padding Background Color")
        padColorLabel.grid(row=7, column=0, sticky=tk.W, padx=4, pady=4)
        padColorEntry = tk.Entry(slideFrame, textvariable=self.inputPadColor)
        padColorEntry.grid(row=7, column=1, sticky=tk.W, padx=4, pady=4)

        transitionFrame = tk.LabelFrame(configFrame, text="Transition")
        transitionFrame.grid(row=7, column=0, sticky=tk.NSEW, padx=4, pady=4)

        self.inputTransitionDuration.set(self.config["fade_duration"])
        transitionDurationLabel = tk.Label(transitionFrame, text="Duration")
        transitionDurationLabel.grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        transitionDurationEntry = tk.Entry(transitionFrame, textvariable=self.inputTransitionDuration)
        transitionDurationEntry.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputTransition.set(self.config["transition"])
        transitionLabel = tk.Label(transitionFrame, text="Transition")
        transitionLabel.grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
        transitionCombo = ttk.Combobox(transitionFrame, values=[
                                       "random"] + choices["transition"], width=30, textvariable=self.inputTransition)
        transitionCombo.grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputTransitionBars.set(self.config["transition_bars_count"])
        transitionBarsLabel = tk.Label(transitionFrame, text="Transition Bars Count")
        transitionBarsLabel.grid(row=2, column=0, sticky=tk.W, padx=4, pady=4)
        transitionBarsEntry = tk.Entry(transitionFrame, textvariable=self.inputTransitionBars)
        transitionBarsEntry.grid(row=2, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputTransitionCells.set(self.config["transition_cell_size"])
        transitionCellsLabel = tk.Label(transitionFrame, text="Transition Cell Size")
        transitionCellsLabel.grid(row=3, column=0, sticky=tk.W, padx=4, pady=4)
        transitionCellsEntry = tk.Entry(transitionFrame, textvariable=self.inputTransitionCells)
        transitionCellsEntry.grid(row=3, column=1, sticky=tk.W, padx=4, pady=4)

        buttonSaveSlide = tk.Button(configFrame, text="Save", command=(lambda: self.saveConfig()))
        buttonSaveSlide.grid(row=8, column=0, sticky=tk.NW, padx=4, pady=4)

        scrollFrame.addFrame(configFrame, tk.NW)

    def getConfig(self):
        return {
            "ffmpeg": self.inputffmpeg.get(),
            "ffprobe": self.inputffprobe.get(),
            "aubio": self.inputAubio.get(),
            "IMAGE_EXTENSIONS": self.config["IMAGE_EXTENSIONS"],
            "VIDEO_EXTENSIONS": self.config["VIDEO_EXTENSIONS"],
            "AUDIO_EXTENSIONS": self.config["AUDIO_EXTENSIONS"],
            "output_width": int(self.inputOutputWidth.get()),
            "output_height": int(self.inputOutputHeight.get()),
            "output_codec": self.inputOutputCodec.get(),
            "output_parameters": self.inputOutputParameters.get(),
            "slide_duration": float(self.inputDuration.get()),
            "slide_duration_min": float(self.inputDurationMin.get()),
            "fade_duration": float(self.inputTransitionDuration.get()),
            "transition": self.inputTransition.get(),
            "transition_bars_count": int(self.inputTransitionBars.get()),
            "transition_cell_size": int(self.inputTransitionCells.get()),
            "fps": int(self.inputFPS.get()),
            "zoom_rate": float(self.inputZoomRate.get()),
            "zoom_direction_x": self.inputZoomDirectionX.get(),
            "zoom_direction_y": self.inputZoomDirectionY.get(),
            "zoom_direction_z": self.inputZoomDirectionZ.get(),
            "scale_mode": self.inputScaleMode.get(),
            "pad_color": self.inputPadColor.get(),
            "loopable": self.inputLoopable.get(),
            "overwrite": self.inputOverwrite.get(),
            "generate_temp": self.inputGenerateTemp.get(),
            "delete_temp": self.inputDeleteTemp.get(),
            "temp_file_folder": self.inputTempFileFolder.get(),
            "temp_file_prefix": self.inputTempFilePrefix.get(),
            "sync_to_audio": self.inputSyncToAudio.get()
        }

    def saveConfig(self):
        logger.info("Save global config")

        config = self.getConfig()

        with open(self.config_path, 'w') as file:
            json.dump(config, file, indent=4)
