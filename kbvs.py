from gui.app import App
import os

import logging

# Logging
logger = logging.getLogger("kburns-slideshow")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(os.path.dirname(os.path.realpath(__file__)) + '/kburns-slideshow-gui.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

if __name__ == "__main__":
    app = App("kbvs")
    app.mainloop()
