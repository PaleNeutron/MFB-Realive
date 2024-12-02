"""
This module provides functions for interacting with the mouse, including mouse clicks, scrolling, and mouse movement within a window.

Functions:
- mouse_click: Perform a mouse click.
- mouse_scroll: Perform a mouse scroll.
- mouse_position: Get the current mouse position relative to a given window.
- move_mouse_and_click: Move the mouse to specified coordinates within a window and perform a click.
- move_mouse: Move the mouse to specified coordinates within a window.

Constants:
- MOUSE_RANGE: The range of random mouse movement.
"""

import logging
import random
import sys
import time

from modules.base_mouse_func import click, moveTo, position, scroll
from modules.humanclicker import HumanClicker
from modules.humancurve import HumanCurve
from modules.utils import rsleep

MOUSE_RANGE = 2


log = logging.getLogger(__name__)

def mouse_click(btn="left"):
    """
    Simulates a mouse click.

    Args:
        btn (str, optional): Specifies the button to click. Defaults to "left".
    """
    click(button=btn)


def mouse_scroll(s):
    """
    Simulates mouse scroll.

    Args:
        s (int): Specifies the amount and direction to scroll. Positive values scroll up, negative values scroll down.
    """
    if s == 0:
        return
    step = s // abs(s)
    for _ in range(0, s, step):
        scroll(step)


def mouse_position(window):
    """
    Retrieves the current mouse position relative to a window.

    Args:
        window (tuple): The (x, y) position of the window's top left corner.

    Returns:
        tuple: The current mouse position relative to the window's top left corner.
    """
    x, y = position()
    return x - window[0], y - window[1]


def move_mouse_and_click(window, x, y):
    """
    Moves the mouse to a specified location relative to a window and simulates a click.

    Args:
        window (tuple): The (x, y) position of the window's top left corner.
        x (int): The x-coordinate for the mouse to move to, relative to the window.
        y (int): The y-coordinate for the mouse to move to, relative to the window.
    """
    move_mouse(window, x, y)
    rsleep(0.05)
    log.info("Clicking at %s, %s", x, y)
    click()


def move_mouse(window, x, y):
    """
    Moves the mouse using Bézier curves to a specified location relative to a window.    Args:
        window (tuple): The (x, y) position of the window's top left corner.
        x (int): The x-coordinate for the mouse to move to, relative to the window.
        y (int): The y-coordinate for the mouse to move to, relative to the window.
    """

    fromPoint = position()
    toPoint = (window[0] + x, window[1] + y)
    hc = HumanClicker()
    options = {
        "knotsCount": 2,
    }

    human_curve = HumanCurve(fromPoint=fromPoint, toPoint=toPoint, **options)
    duration = random.uniform(0.33, 0.97)

    try:
        hc.move((x, y), duration=duration, humanCurve=human_curve)
    except Exception:
        hc.move((x, y), duration=duration, humanCurve=human_curve)
