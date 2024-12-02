"""
This module contains functions related to entering the game from Battle.net.
"""

import logging
import platform
import re
import subprocess
import time

import pyautogui
import pygetwindow as gw

from modules.constants import Action, Button
from modules.image_utils import find_element
from modules.platforms import win
from modules.utils import rsleep

log = logging.getLogger(__name__)


def bring_to_focus_windows():
    """
    Brings a window with either Battle.net or Battle.net.exe as the process name into focus on Windows.

    This function searches for all windows that match the process name and brings the window into focus.
    If an error occurs during the process, it logs the error message.
    """
    try:
        from win32 import win32process
        # Run a WMIC command to get the process id
        output = subprocess.check_output(
            "wmic process where (name='Battle.net.exe' or name='Battle.net') get ProcessId", shell=True).decode(
            "utf-8")
        pid = int(re.findall(r'\d+', output)[0])

        # Get list of all windows that match the pid
        windows = gw.getAllWindows( )

        for window in windows:
            _threadid,wpid = win32process.GetWindowThreadProcessId(window._hWnd)
            if wpid == pid:
                # Use the PyAutoGUI library to move the mouse to the center of the window
                pyautogui.moveTo(window.left + window.width / 2, window.top + window.height / 2)

                # Bring the window into focus
                window.activate( )

    except Exception as e:
        log.error(f"Failed to bring window with PID Battle.net.exe or Battle.net to focus. Error: {str(e)}")


def bring_to_focus_linux():
    """
    Brings a window with either Battle.net or Battle.net.exe as the process name into focus on Linux.

    This function uses the ps, wmctrl, and xdotool commands to search for the process and bring the window into focus.
    If an error occurs during the process, it logs the error message.
    """
    try:
        # Use ps aux to get the process id
        output = subprocess.check_output("ps aux | grep -E 'Battle.net|Battle.net.exe'", shell=True).decode("utf-8")
        pid = int(re.findall(r'\d+', output)[0])

        # Use wmctrl and xdotool to bring the window to the foreground
        subprocess.call(['wmctrl', '-ia', str(pid)])
        subprocess.call(['xdotool', 'windowactivate', str(pid)])

    except Exception as e:
        log.error(f"Failed to bring window with PID Battle.net or Battle.net.exe to focus. Error: {str(e)}")


# if platform.system( ) == 'Windows':
#     bring_to_focus_windows( )
# elif platform.system( ) == 'Linux':
#     bring_to_focus_linux( )


def enter_from_battlenet():
    """
    Enters the game from the Battle.net application.
    """
    found_element = find_element(Button.battlenet.filename, Action.move_and_click)
    if found_element:
        rsleep(1)

    found_element = find_element(
        Button.battlenet_hearthstone.filename, Action.move_and_click
    )
    if found_element:
        rsleep(1)

    if find_element(Button.battlenet_play.filename, Action.move_and_click):
        log.info("Waiting (20s) for game to start")
        rsleep(20)

    else:
        log.info("Battle.net wasn't found, attempting to snap to process.")
        win.activate_window()
        rsleep(3)

    return True
