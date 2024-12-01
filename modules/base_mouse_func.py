import sys

import pyautogui
import pydirectinput

if sys.platform != "nothing":
    click = pydirectinput.click
    move = pydirectinput.move
    scroll = pydirectinput.scroll
    position = pydirectinput.position
    moveTo = pydirectinput.moveTo
else:
    click = pyautogui.click
    move = pyautogui.move
    scroll = pyautogui.scroll
    position = pyautogui.position
    moveTo = pyautogui.moveTo