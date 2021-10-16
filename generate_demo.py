#!/usr/bin/env python3

import os
import json

from slideshow.SlideManager import SlideManager

import pkgutil

if __name__ == "__main__":

    config = {}
    with open(os.path.dirname(os.path.realpath(__file__)) + '/config.json') as config_file:
        config = json.load(config_file)

    config.update({
        "output_width": 400,
        "output_height": 250,
        "output_codec": "",
        "output_parameters": "",
        "slide_duration": 2,
        "slide_duration_min": 1,
        "fade_duration": 1.0,
        "transition_bars_count": 10,
        "transition_cell_size": 50,
        "fps": 30,
        "overwrite": True
    })

    transitions = [package_name for importer, package_name, _ in pkgutil.iter_modules(["transitions"])]

    for transition in transitions:
        input_files = [{
            "file": "docs\\media\\andrey-andreyev-dh8ONmfQyQQ-unsplash.jpg",
            "transition": transition,
            "title": transition,
            "zoom_direction_x": "center",
            "zoom_direction_y": "center",
            "zoom_direction_z": "none",
            "scale_mode": "pad"
        },
            {
            "file": "docs\\media\\jeremy-bishop-h7bQ8VEZtws-unsplash.jpg",
            "title": transition,
            "zoom_direction_x": "center",
            "zoom_direction_y": "center",
            "zoom_direction_z": "none",
            "scale_mode": "pad"
        }]

        sm = SlideManager(config, input_files, [])

        sm.createVideo("docs\\demo\\%s.gif" % (transition))
