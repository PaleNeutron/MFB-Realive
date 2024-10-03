import logging
import os
from datetime import datetime

"""
This module provides functions related to choosing treasures after a battle/fight.

Functions:
- choose_treasure: Choose a treasure after a battle/fight.

Note: This module requires the 'random', 'time', and 'queue' libraries.
"""

import logging
import random
import time
from queue import PriorityQueue

import cv2

from modules.constants import Action, Button, UIElement
from modules.image_utils import find_element
from modules.mouse_utils import move_mouse_and_click
from modules.platforms import windowMP
from modules.settings import settings_dict, treasures_priority

from .constants import Action, Button, UIElement
from .image_utils import get_resolution, partscreen
from .mouse_utils import move_mouse_and_click
from .platforms import windowMP
from .settings import settings_dict, treasures_priority

log = logging.getLogger(__name__)

TREASURES_DIR = "treasures"


def chooseTreasure():
    """
    Choose a treasure after a battle/fight.

    Note:
    Treasures are added to a queue (FIFO); if no matches are found, a random treasure is selected.
    """
    treasures_queue = PriorityQueue()

    for treasure in treasures_priority:
        treasures_queue.put((treasures_priority[treasure], treasure))

    log.debug(f"treasures queue contains : {treasures_queue}")

    # capture current screen and save it to logs/treasures
    ## first ensure the directory exists
    ## then capture the screen
    if log.level <= logging.DEBUG:
        treasure_log_dir = "logs/treasures"
        if not os.path.exists(treasure_log_dir):
            os.makedirs(treasure_log_dir)
        
        ## capture the screen
        log.debug("Capturing screen for treasure selection")
        resolution, width, height, scale_size = get_resolution()
        part_Image = partscreen(
                windowMP()[2],
                windowMP()[3],
                windowMP()[1],
                windowMP()[0],
                resize_width=width,
                resize_height=height,
            )
        time_stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        cv2.imwrite(f"{treasure_log_dir}/{time_stamp}.png", part_Image)

    while not treasures_queue.empty():
        next_treasure = treasures_queue.get()[1]

        treasure = str(f"{TREASURES_DIR}/{next_treasure}.png")

        if find_element(treasure, Action.move_and_click):
            time.sleep(1)
            break
    else:
        found = False
        if settings_dict["preferpassivetreasures"] is True:
            log.info("No known treasure found: looking for passive one")
            if find_element(UIElement.treasure_passive.filename, Action.move_and_click):
                found = True
                time.sleep(1)

        if found is False:
            log.info("No known treasure found: picking random one")
            temp = random.choice([2.3, 1.7, 1.4])
            y = windowMP()[3] // 2
            x = windowMP()[2] // temp
            move_mouse_and_click(windowMP(), x, y)
            time.sleep(1)

    while not (
        find_element(Button.take.filename, Action.move_and_click)
        or find_element(Button.keep.filename, Action.move_and_click)
        or find_element(Button.replace.filename, Action.move_and_click)
    ):
        time.sleep(1)
