import logging
import os
import json

import slideshow.cli as cli
from slideshow.SlideManager import SlideManager

# Logging
logger = logging.getLogger("kburns-slideshow")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler( os.path.dirname(os.path.realpath(__file__)) + '/kburns-slideshow.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


if __name__ == "__main__":

    config = {}
    with open('slideshow/config.json') as config_file:
        config = json.load(config_file)    
    
    command_line = cli.CLI(config)
    config, input_files, audio_files, output_file = command_line.parse()

    sm = SlideManager(config, input_files, audio_files)

    sm.createVideo(output_file)