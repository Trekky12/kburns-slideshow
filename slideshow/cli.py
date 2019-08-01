import argparse
import itertools
import json
import os
import sys

class CLI:

    def __init__(self, config):
        self.config = config
        
        self.parser = argparse.ArgumentParser()

        self.parser.add_argument("-s", "--size", metavar='WIDTHxHEIGHT', help="Output width (default: %sx%s)" %(self.config["output_width"], self.config["output_height"]))
        self.parser.add_argument("-sd", "--slide-duration", metavar='DURATION', type=float, help="Slide duration (seconds) (default: %s)" %(self.config["slide_duration"]))
        self.parser.add_argument("-fd", "--fade-duration", metavar='DURATION', type=float, help="Fade duration (seconds) (default: %s)" %(self.config["fade_duration"]))
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
        
        self.parser.add_argument("input_files", nargs='*')
        self.parser.add_argument("output_file")
        
        
    def parse(self):
        args = self.parser.parse_args()
            
        if args.size is not None:
            size = args.size.split("x")
            self.config["output_width"] = int(size[0])
            self.config["output_height"] = int(size[1])
         
        if args.slide_duration is not None: 
            self.config["slide_duration"] = args.slide_duration

        if args.fade_duration is not None: 
            self.config["fade_duration"] = args.fade_duration    
            
        if args.fps is not None: 
            self.config["fps"] = args.fps    

        if args.zoom_direction is not None:
            self.config["zoom_direction"] = args.zoom_direction       
            
        if args.zoom_rate is not None:
            self.config["zoom_rate"] = args.zoom_rate    
            
        if args.scale_mode is not None:
            self.config["scale_mode"] = args.scale_mode
            
        self.config["loopable"] = args.loopable
        self.config["overwrite"] = args.y
        self.config["generate_temp"] = args.temp
        self.config["delete_temp"] = args.delete_temp
        
        audio = []
        if args.audio is not None:
            audio = args.audio    
        
        return self.config, args.input_files, audio, args.output_file