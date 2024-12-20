import subprocess
import time

import psutil

from modules.battlenetloop import enter_from_battlenet
from modules.mouse_utils import move_mouse_and_click
from modules.platforms import windowMP
from modules.utils import rsleep


def choose_mode():
    """
    This is to address the new Menu released 6.28.23
    Blizzard moved Mercenaries into Modes menu
    """
    mode_coord_x = 1337 / 1920
    mode_coord_y = 276 / 1080
    choose_coord_x = 1367 / 1920
    choose_coord_y = 750 / 1080

    move_mouse_and_click(windowMP( ), windowMP( )[2] * mode_coord_x, windowMP( )[3] * mode_coord_y)
    rsleep(1)
    move_mouse_and_click(windowMP( ), windowMP( )[2] * choose_coord_x, windowMP( )[3] * choose_coord_y)


def click_wipe_button():
    """
    This is to address a popup that occurs when your party dies sometimes:
    A Valiant Effort
    Your party was wiped out.

    The click coords may be off and still requires testing.
    """
    wipe_coord_x = 948 / 1920
    wipe_coord_y = 647 / 1080

    move_mouse_and_click(windowMP( ), windowMP( )[2] * wipe_coord_x, windowMP( )[3] * wipe_coord_y)
    rsleep(0.3)


def click_reconnect():
    """
    This is to reconnect at the screen that says:
    You are currently offline
    It's been awhile since your last Hearthstone action and your connection was shut down.

    Usually it's called multiple times as the screen can appear back to back after clicking reconnect.
    """
    rcbutton_coord_x = 773 / 1920
    rcbutton_coord_y = 840 / 1080

    move_mouse_and_click(windowMP( ), windowMP( )[2] * rcbutton_coord_x, windowMP( )[3] * rcbutton_coord_y)
    rsleep(0.3)


def game_closed():
    """
    This function is to address the message:
    Closed
    It's been a while since your last Hearthstone action
    and your connection was shut down.
    Relaunch the game when you're ready!
    Or
    Oops! Playful sprites have disrupted Hearthstone as it
    was connecting to our servers. Please wait for a few minutes
    for them to disperse and try again.

    First it attempts to use psutil to kill the process;
    then it attempts OS specific commands before trying to relaunch the game.
    """
    process_name = "hearthstone.exe"
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            pid = proc.info["pid"]
            try:
                proc.kill()
                rsleep(1)  # give the process some time to terminate
                if not psutil.pid_exists(pid):
                    print(f'Process {process_name} with PID {pid} was successfully killed with psutil.')
                    return
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                print(f'Unable to kill process {process_name} with PID {pid} using psutil.')

            commands = [
                (["taskkill", "/F", "/PID", str(pid)], 'taskkill (PID)'),
                (["kill", "-9", str(pid)], 'kill (PID)'),
                (["taskkill", "/IM", process_name, "/F"], 'taskkill (name)'),
                (["pkill", "-9", process_name], 'pkill (name)')
            ]

            for command, method in commands:
                try:
                    subprocess.run(command)
                    rsleep(1)  # give the process some time to terminate
                    if not psutil.pid_exists(pid):
                        print(f'Process {process_name} was successfully killed with {method}.')
                        return
                except Exception:
                    print(f'Unable to kill process {process_name} using {method}.')

            print(f'Failed to kill process {process_name} with PID {pid}.')

    rsleep(2)
    enter_from_battlenet()
