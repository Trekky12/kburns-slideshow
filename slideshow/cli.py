import argparse
import itertools
import json
import os
import sys
import logging
import pkgutil

logger = logging.getLogger("kburns-slideshow")

class CLI:

    def __init__(self, config):
        self.config = config
        
        logger.debug("Init CLI")
        
        self.parser = argparse.ArgumentParser()

        self.parser.add_argument("-S", "--size", metavar='WIDTHxHEIGHT', help="Output width (default: %sx%s)" %(self.config["output_width"], self.config["output_height"]))
        self.parser.add_argument("-sd", "--slide-duration", metavar='DURATION', type=float, help="Slide duration (seconds) (default: %s)" %(self.config["slide_duration"]))
        self.parser.add_argument("-sdm", "--slide-duration-min", metavar='DURATION', type=float, help="Slide duration minimum (seconds) (default: %s)" %(self.config["slide_duration_min"]))
        self.parser.add_argument("-fd", "--fade-duration", metavar='DURATION', type=float, help="Fade duration (seconds) (default: %s)" %(self.config["fade_duration"]))
        
        transition_choices = [package_name for importer, package_name, _ in pkgutil.iter_modules([os.path.dirname(os.path.realpath(__file__))+"/effects"])]
        self.parser.add_argument("-ft", "--fade-transition", metavar='TRANSITION', choices=transition_choices, help="Fade transition (default: %s)" %(self.config["transition"]))
        
        self.parser.add_argument("-fps", "--fps", metavar='FPS', type=int, help="Output framerate (frames per second) (default: %s)" %(self.config["fps"]))

        zoom_direction_possibilities = [["top", "center", "bottom"], ["left", "center", "right"], ["in", "out"]]
        zoom_direction_choices = ["random"] + list(map(lambda x: "-".join(x), itertools.product(*zoom_direction_possibilities)))
        self.parser.add_argument("-zd", "--zoom-direction", metavar='DIRECTION', choices=zoom_direction_choices, help="Zoom direction (default: %s)" %(self.config["zoom_direction"]))

        self.parser.add_argument("-zr", "--zoom-rate", metavar='RATE', type=float, help="Zoom rate (default:  %s)" %(self.config["zoom_rate"]))
        self.parser.add_argument("-sm", "--scale-mode", metavar='SCALE_MODE', choices=["auto", "pad", "pan", "crop_center"], help="Scale mode (pad, crop_center, pan) (default: %s)" %(self.config["scale_mode"]))
        self.parser.add_argument("-l", "--loopable", action='store_true', help="Create loopable video")
        self.parser.add_argument("-y", action='store_true', help="Overwrite output file without asking")
        
        self.parser.add_argument("-t", "--temp", action='store_true', help="Generate temporary files")
        self.parser.add_argument("-d", "--delete-temp", action='store_true', help="Generate temporary files")

        self.parser.add_argument("-a", "--audio", metavar='FILE', help="One or more background audio tracks", nargs='*')
        
        self.parser.add_argument("-i", "--input-files", metavar='FILE', help="One or more input files", nargs='+')
        self.parser.add_argument("-f", "--file-list", metavar='LIST',)
        
        self.parser.add_argument("-s", "--save", metavar='FILE', help="save settings")
        
        self.parser.add_argument("output_file")
        
        
    def parse(self):
        args = self.parser.parse_args()
            
        input_files = []
        audio_files = []
        
        if args.input_files is not None:
            input_files = args.input_files
            logger.debug("Load Files from command line: %s", input_files)
        
        elif args.file_list is not None:
            logger.debug("Load from file: %s", args.file_list)
            try:
                with open(args.file_list) as f:
                    file_content = json.load(f)    
                    
                    # overwrite config with saved config
                    if "config" in file_content:
                        self.config.update(file_content["config"])
                        logger.debug("overwrite config")
                    
                    # get slides from loaded file
                    if "slides" in file_content:
                        input_files = file_content["slides"]
                        logger.debug("get slides")
                    
                    if "audio" in file_content:
                        audio_files = file_content["audio"]
                        logger.debug("get audio")
            except:
                self.parser.error("file must be a JSON file")
                logger.error("file %s must be a JSON file", args.file_list)
        
        if len(input_files) == 0:
            self.parser.error("no input files specified")
            logger.error("no input files specified")
            
        if args.size is not None:
            size = args.size.split("x")
            self.config["output_width"] = int(size[0])
            self.config["output_height"] = int(size[1])
            logger.debug("Set size to %sx%s", int(size[0]), int(size[1]))
         
        if args.slide_duration is not None: 
            self.config["slide_duration"] = args.slide_duration
            logger.debug("Set slide duration to %s", args.slide_duration)
            
        if args.slide_duration_min is not None: 
            self.config["slide_duration_min"] = args.slide_duration_min
            logger.debug("Set min slide duration to %s", args.slide_duration_min)

        if args.fade_duration is not None: 
            self.config["fade_duration"] = args.fade_duration
            logger.debug("Set fade duration to %s", args.fade_duration)
            
        if args.fade_transition is not None:
            self.config["transition"] = args.fade_transition
            logger.debug("Set transition to %s", args.fade_transition)
            
        if args.fps is not None: 
            self.config["fps"] = args.fps    
            logger.debug("Set fps to %s", args.fps)

        if args.zoom_direction is not None:
            self.config["zoom_direction"] = args.zoom_direction
            logger.debug("Set zoom direction to %s", args.zoom_direction)
            
        if args.zoom_rate is not None:
            self.config["zoom_rate"] = args.zoom_rate
            logger.debug("Set zoom rate to %s", args.zoom_rate)
            
        if args.scale_mode is not None:
            self.config["scale_mode"] = args.scale_mode
            logger.debug("Set scale mode to %s", args.scale_mode)
            
        if args.loopable is True:
            self.config["loopable"] = True
            logger.debug("Set loopable")
            
        if args.y is True:
            self.config["overwrite"] = True
            logger.debug("Set overwrite")
            
        if args.temp is True:
            self.config["generate_temp"] = True
            logger.debug("Set generate temporary files")
            
        if args.delete_temp is True:
            self.config["delete_temp"] = True
            logger.debug("Set delete temporary files")
        
        if args.audio is not None:
            audio_files.extend(args.audio)
            logger.debug("Load audio files from command line: %s", args.audio)
        
        self.config["save"] = args.save
        
        logger.debug("Save config: %s", args.save)
        
        return self.config, input_files, audio_files, args.output_file