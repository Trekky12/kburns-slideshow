#!/usr/bin/env python3

import logging
import os
import json

import slideshow.cli as cli
from slideshow.SlideManager import SlideManager

# Logging
logger = logging.getLogger("kburns-slideshow")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(os.path.dirname(os.path.realpath(__file__)) + '/kburns-slideshow.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


if __name__ == "__main__":

    config = {}
    with open(os.path.dirname(os.path.realpath(__file__)) + '/config.json') as config_file:
        config = json.load(config_file)

    command_line = cli.CLI(config)
    config, input_files, audio_files, output_file = command_line.parse()

    sm = SlideManager(config, input_files, audio_files)

    if config["sync_to_audio"]:
        logger.info("Sync slides durations to audio")
        sm.adjustDurationsFromAudio()

    if config["sync_titles_to_slides"]:
        logger.info("Sync titles durations to slides durations")
        sm.adjustTitlesToSlides()

    sm.createVideo(output_file, True, config["save"], config["test"], config["overwrite"])
