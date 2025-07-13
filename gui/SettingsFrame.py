import tkinter as tk
from tkinter import ttk

import logging

from .ScrollFrame import ScrollFrame

logger = logging.getLogger("kburns-slideshow")


class SettingsFrame(tk.Toplevel):
    def __init__(self, parent, **options):
        super().__init__()

        self.inputLoopable = tk.BooleanVar()
        self.inputOverwrite = tk.BooleanVar()
        self.inputGenerateTemp = tk.BooleanVar()
        self.inputDeleteTemp = tk.BooleanVar()
        self.inputOutputTempParameters = tk.StringVar()
        self.inputOutputTempCodec = tk.StringVar()
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

        self.slideshow_config = {}

    def create(self, slideshow_config, choices):

        self.slideshow_config = slideshow_config

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.geometry("700x700")

        scrollFrame = ScrollFrame(self, 200, True)
        scrollFrame.grid(row=0, column=0, sticky=tk.NSEW)

        configFrame = tk.Frame(scrollFrame.getCanvas())
        configFrame.columnconfigure(0, weight=1)

        outputFrame = tk.LabelFrame(configFrame, text="Output")
        outputFrame.grid(row=1, column=0, sticky=tk.NSEW, padx=4, pady=4)
        outputFrame.columnconfigure(1, weight=1)

        self.inputOutputWidth.set(slideshow_config["output_width"])
        widthLabel = tk.Label(outputFrame, text="Width")
        widthLabel.grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        widthEntry = tk.Entry(outputFrame, textvariable=self.inputOutputWidth)
        widthEntry.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputOutputHeight.set(slideshow_config["output_height"])
        heightLabel = tk.Label(outputFrame, text="Height")
        heightLabel.grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
        heightEntry = tk.Entry(outputFrame, textvariable=self.inputOutputHeight)
        heightEntry.grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputOutputParameters.set(slideshow_config["output_parameters"])
        parametersLabel = tk.Label(outputFrame, text="Parameters")
        parametersLabel.grid(row=2, column=0, sticky=tk.W, padx=4, pady=4)
        parametersEntry = tk.Entry(outputFrame, width=67, textvariable=self.inputOutputParameters)
        parametersEntry.grid(row=2, column=1, columnspan=3, sticky=tk.EW, padx=4, pady=4)

        self.inputOutputCodec.set(slideshow_config["output_codec"])
        codecLabel = tk.Label(outputFrame, text="Codec")
        codecLabel.grid(row=3, column=0, sticky=tk.W, padx=4, pady=4)
        codecEntry = tk.Entry(outputFrame, textvariable=self.inputOutputCodec)
        codecEntry.grid(row=3, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputFPS.set(slideshow_config["fps"])
        fpsLabel = tk.Label(outputFrame, text="FPS")
        fpsLabel.grid(row=4, column=0, sticky=tk.W, padx=4, pady=4)
        fpsEntry = tk.Entry(outputFrame, textvariable=self.inputFPS)
        fpsEntry.grid(row=4, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputLoopable.set(slideshow_config["loopable"])
        loopableLabel = tk.Label(outputFrame, text="Loopable")
        loopableLabel.grid(row=5, column=0, sticky=tk.W, padx=4, pady=4)
        loopableCheckBox = tk.Checkbutton(outputFrame, var=self.inputLoopable)
        loopableCheckBox.grid(row=5, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputOverwrite.set(slideshow_config["overwrite"])
        overwriteLabel = tk.Label(outputFrame, text="Overwrite")
        overwriteLabel.grid(row=6, column=0, sticky=tk.W, padx=4, pady=4)
        overwriteCheckBox = tk.Checkbutton(outputFrame, var=self.inputOverwrite)
        overwriteCheckBox.grid(row=6, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputSyncToAudio.set(slideshow_config["sync_to_audio"])
        syncToAudioLabel = tk.Label(outputFrame, text="Sync to Audio")
        syncToAudioLabel.grid(row=7, column=0, sticky=tk.W, padx=4, pady=4)
        syncToAudioCheckBox = tk.Checkbutton(outputFrame, var=self.inputSyncToAudio)
        syncToAudioCheckBox.grid(row=7, column=1, sticky=tk.W, padx=4, pady=4)

        tempFrame = tk.LabelFrame(configFrame, text="Temporary files")
        tempFrame.grid(row=2, column=0, sticky=tk.NSEW, padx=4, pady=4)
        tempFrame.columnconfigure(1, weight=1)

        self.inputTempFileFolder.set(slideshow_config["temp_file_folder"])
        tempFileFolderLabel = tk.Label(tempFrame, text="Folder")
        tempFileFolderLabel.grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        tempFileFolderEntry = tk.Entry(tempFrame, textvariable=self.inputTempFileFolder)
        tempFileFolderEntry.grid(row=0, column=1, sticky=tk.EW, padx=4, pady=4)

        self.inputTempFilePrefix.set(slideshow_config["temp_file_prefix"])
        tempFilePrefixLabel = tk.Label(tempFrame, text="Prefix")
        tempFilePrefixLabel.grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
        tempFilePrefixEntry = tk.Entry(tempFrame, textvariable=self.inputTempFilePrefix)
        tempFilePrefixEntry.grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputGenerateTemp.set(slideshow_config["generate_temp"])
        generateTempLabel = tk.Label(tempFrame, text="Generate")
        generateTempLabel.grid(row=2, column=0, sticky=tk.W, padx=4, pady=4)
        generateTempCheckBox = tk.Checkbutton(tempFrame, var=self.inputGenerateTemp)
        generateTempCheckBox.grid(row=2, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputDeleteTemp.set(slideshow_config["delete_temp"])
        deleteTempLabel = tk.Label(tempFrame, text="Delete")
        deleteTempLabel.grid(row=3, column=0, sticky=tk.W, padx=4, pady=4)
        deleteTempCheckBox = tk.Checkbutton(tempFrame, var=self.inputDeleteTemp)
        deleteTempCheckBox.grid(row=3, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputOutputTempParameters.set(self.slideshow_config["output_temp_parameters"])
        tempParametersLabel = tk.Label(tempFrame, text="Parameters")
        tempParametersLabel.grid(row=4, column=0, sticky=tk.W, padx=4, pady=4)
        tempParametersEntry = tk.Entry(tempFrame, width=67, textvariable=self.inputOutputTempParameters)
        tempParametersEntry.grid(row=4, column=1, columnspan=3, sticky=tk.EW, padx=4, pady=4)

        self.inputOutputTempCodec.set(self.slideshow_config["output_temp_codec"])
        tempCodecLabel = tk.Label(tempFrame, text="Codec")
        tempCodecLabel.grid(row=5, column=0, sticky=tk.W, padx=4, pady=4)
        tempCodecEntry = tk.Entry(tempFrame, textvariable=self.inputOutputTempCodec)
        tempCodecEntry.grid(row=5, column=1, sticky=tk.W, padx=4, pady=4)

        slideFrame = tk.LabelFrame(configFrame, text="Image Slides")
        slideFrame.grid(row=3, column=0, sticky=tk.NSEW, padx=4, pady=4)

        self.inputDuration.set(slideshow_config["slide_duration"])
        durationLabel = tk.Label(slideFrame, text="Duration")
        durationLabel.grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        durationEntry = tk.Entry(slideFrame, textvariable=self.inputDuration)
        durationEntry.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputDurationMin.set(slideshow_config["slide_duration_min"])
        durationMinLabel = tk.Label(slideFrame, text="Duration (min)")
        durationMinLabel.grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
        durationMinEntry = tk.Entry(slideFrame, textvariable=self.inputDurationMin)
        durationMinEntry.grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputZoomRate.set(slideshow_config["zoom_rate"])
        zoomRateLabel = tk.Label(slideFrame, text="Zoom Rate")
        zoomRateLabel.grid(row=2, column=0, sticky=tk.W, padx=4, pady=4)
        zoomRateEntry = tk.Entry(slideFrame, textvariable=self.inputZoomRate)
        zoomRateEntry.grid(row=2, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputZoomDirectionX.set(slideshow_config["zoom_direction_x"])
        zoomDirectionXLabel = tk.Label(slideFrame, text="Zoom Direction X")
        zoomDirectionXLabel.grid(row=3, column=0, sticky=tk.W, padx=4, pady=4)
        zoomDirectionXCombo = ttk.Combobox(slideFrame, values=choices["zoom_direction_x"],
                                           textvariable=self.inputZoomDirectionX)
        zoomDirectionXCombo.grid(row=3, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputZoomDirectionY.set(slideshow_config["zoom_direction_y"])
        zoomDirectionYLabel = tk.Label(slideFrame, text="Zoom Direction Y")
        zoomDirectionYLabel.grid(row=4, column=0, sticky=tk.W, padx=4, pady=4)
        zoomDirectionYCombo = ttk.Combobox(slideFrame, values=choices["zoom_direction_x"],
                                           textvariable=self.inputZoomDirectionY)
        zoomDirectionYCombo.grid(row=4, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputZoomDirectionZ.set(slideshow_config["zoom_direction_z"])
        zoomDirectionZLabel = tk.Label(slideFrame, text="Zoom Direction Z")
        zoomDirectionZLabel.grid(row=5, column=0, sticky=tk.W, padx=4, pady=4)
        zoomDirectionZCombo = ttk.Combobox(slideFrame, values=choices["zoom_direction_x"],
                                           textvariable=self.inputZoomDirectionZ)
        zoomDirectionZCombo.grid(row=5, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputScaleMode.set(slideshow_config["scale_mode"])
        scaleModeLabel = tk.Label(slideFrame, text="Scale Mode")
        scaleModeLabel.grid(row=6, column=0, sticky=tk.W, padx=4, pady=4)
        scaleModeCombo = ttk.Combobox(slideFrame, values=choices["scale_mode"], textvariable=self.inputScaleMode)
        scaleModeCombo.grid(row=6, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputPadColor.set(slideshow_config["pad_color"])
        padColorLabel = tk.Label(slideFrame, text="Padding Background Color")
        padColorLabel.grid(row=7, column=0, sticky=tk.W, padx=4, pady=4)
        padColorEntry = tk.Entry(slideFrame, textvariable=self.inputPadColor)
        padColorEntry.grid(row=7, column=1, sticky=tk.W, padx=4, pady=4)

        transitionFrame = tk.LabelFrame(configFrame, text="Transition")
        transitionFrame.grid(row=7, column=0, sticky=tk.NSEW, padx=4, pady=4)

        self.inputTransitionDuration.set(slideshow_config["fade_duration"])
        transitionDurationLabel = tk.Label(transitionFrame, text="Duration")
        transitionDurationLabel.grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        transitionDurationEntry = tk.Entry(transitionFrame, textvariable=self.inputTransitionDuration)
        transitionDurationEntry.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputTransition.set(slideshow_config["transition"])
        transitionLabel = tk.Label(transitionFrame, text="Transition")
        transitionLabel.grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
        transitionCombo = ttk.Combobox(transitionFrame, values=[
                                       "random"] + choices["transition"], width=30, textvariable=self.inputTransition)
        transitionCombo.grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputTransitionBars.set(slideshow_config["transition_bars_count"])
        transitionBarsLabel = tk.Label(transitionFrame, text="Transition Bars Count")
        transitionBarsLabel.grid(row=2, column=0, sticky=tk.W, padx=4, pady=4)
        transitionBarsEntry = tk.Entry(transitionFrame, textvariable=self.inputTransitionBars)
        transitionBarsEntry.grid(row=2, column=1, sticky=tk.W, padx=4, pady=4)

        self.inputTransitionCells.set(slideshow_config["transition_cell_size"])
        transitionCellsLabel = tk.Label(transitionFrame, text="Transition Cell Size")
        transitionCellsLabel.grid(row=3, column=0, sticky=tk.W, padx=4, pady=4)
        transitionCellsEntry = tk.Entry(transitionFrame, textvariable=self.inputTransitionCells)
        transitionCellsEntry.grid(row=3, column=1, sticky=tk.W, padx=4, pady=4)

        scrollFrame.addFrame(configFrame, tk.NW)

    def getConfig(self):
        return {
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
            "output_temp_parameters": self.inputOutputTempParameters.get(),
            "output_temp_codec": self.inputOutputTempCodec.get(),
            "temp_file_folder": self.inputTempFileFolder.get(),
            "temp_file_prefix": self.inputTempFilePrefix.get(),
            "sync_to_audio": self.inputSyncToAudio.get()
        }
