import sys

import pyautogui

if sys.platform == "nothing":
    import pydirectinput

    click = pydirectinput.click
    move = pydirectinput.move
    scroll = pydirectinput.scroll
    position = pydirectinput.position
    moveTo = pydirectinput.moveTo
else:

    def my_click(
        x=None,
        y=None,
        clicks=1,
        interval=0.0,
        button="primary",
        duration=0.1,
        logScreenshot=None,
        _pause=True,
    ):
        pyautogui.click(
            x=x,
            y=y,
            clicks=clicks,
            interval=interval,
            button=button,
            duration=duration,
            logScreenshot=logScreenshot,
            _pause=_pause,
        )
    click = pyautogui.click
    move = pyautogui.move
    scroll = pyautogui.scroll
    position = pyautogui.position
    moveTo = pyautogui.moveTo
    dragTo = pyautogui.dragTo
