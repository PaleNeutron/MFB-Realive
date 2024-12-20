"""
This module contains functions related to moving from one bounty to the next, quitting when specified, and finding and moving in-between game windows.
"""
import json
import logging
import pathlib
import random
import sys
import time

from modules.campfire import look_at_campfire_completed_tasks
from modules.constants import Action, Button, UIElement
from modules.encounter import selectCardsInHand
from modules.game import defaultCase, wait_until_timeout
from modules.image_utils import find_element
from modules.mouse_utils import (
    MOUSE_RANGE,
    mouse_click,
    mouse_position,
    move_mouse,
    move_mouse_and_click,
)
from modules.notification import send_notification, send_slack_notification
from modules.platforms import windowMP
from modules.settings import jthreshold, settings_dict
from modules.treasure import chooseTreasure
from modules.utils import rsleep

log = logging.getLogger(__name__)


def collect():
    """
    Collect the rewards just after beating the final boss of this level
    """

    # it's difficult to find every boxes with lib CV2 so,
    # we try to detect just one and then we click on all known positions
    collectAttempts = 0

    while True:
        collectAttempts += 1

        positions = [
            (2.5, 3.5),
            (2, 3.5),
            (1.5, 3.5),
            (1.5, 2.4),
            (2.7, 1.4),
            (3, 2.7),
            (1.4, 1.3),
            (1.6, 1.3),
            (1.7, 1.3),
            (1.8, 1.3),
            (1.9, 1.3),
        ]

        for x, y in positions:
            move_mouse_and_click(windowMP(), windowMP()[2] / x, windowMP()[3] / y)

        # click done button in middle
        move_mouse_and_click(windowMP(), windowMP()[2] / 1.9, windowMP()[3] / 1.8)

        # move the mouse to avoid a bug where it is over a card/hero (at the end)
        # hiding the "OK" button
        move_mouse(windowMP(), windowMP()[2] // 1.25, windowMP()[3] // 1.25)
        rsleep(5)

        if find_element(Button.finishok.filename, Action.move_and_click):
            break

        if collectAttempts > 10:
            send_notification(
                {
                    "message": f"Attempted to collect treasure {collectAttempts} times, attempting to recover."
                }
            )
            send_slack_notification(
                json.dumps(
                    {
                        "text": f"@channel Attempted to collect treasure {collectAttempts} times, attempting to recover."
                    }
                )
            )
            log.info(
                "Attempted to collect treasure %s times, attempting to recover.",
                collectAttempts,
            )
            break


def quitBounty():
    """
    Function to (auto)quit the bounty. Called if the user configured it.
    """
    end = False
    if find_element(Button.view_party.filename, Action.move_and_click):
        while not find_element(UIElement.your_party.filename, Action.move):
            rsleep(0.5)
        while not find_element(Button.retire.filename, Action.move_and_click):
            rsleep(0.5)
        while not find_element(Button.lockin.filename, Action.move_and_click):
            rsleep(0.5)
        end = True
        log.info("Quitting the bounty level before boss battle.")
    return end


def nextlvl():
    """
    Progress on the map (Boon, Portal, ...) to find the next battle
    """
    rsleep(3)
    retour = True

    if not find_element(Button.play.filename, Action.screenshot):
        if (
            find_element(UIElement.task_completed.filename, Action.screenshot)
            or find_element(UIElement.task_event_completed.filename, Action.screenshot)
            or find_element(
                UIElement.task_expansion_completed.filename, Action.screenshot
            )
        ):
            wait_until_timeout(UIElement.campfire, 10)
            look_at_campfire_completed_tasks()

        elif find_element(Button.reveal.filename, Action.move_and_click):
            rsleep(1)
            move_mouse_and_click(windowMP(), windowMP()[2] / 2, windowMP()[3] // 1.25)
            rsleep(1.5)

        elif find_element(Button.visit.filename, Action.move_and_click):
            rsleep(7)

        elif find_element(Button.pick.filename, Action.move_and_click) or find_element(
            Button.portal_warp.filename, Action.move_and_click
        ):
            rsleep(1)
            mouse_click()
            rsleep(5)
        elif find_element(UIElement.mystery.filename, Action.screenshot):
            rsleep(1)
            find_element(UIElement.mystery.filename, Action.move_and_click)

        elif find_element(UIElement.spirithealer.filename, Action.screenshot):
            rsleep(1)
            find_element(UIElement.spirithealer.filename, Action.move_and_click)

        elif find_element(UIElement.campfire.filename, Action.screenshot):
            look_at_campfire_completed_tasks()
            rsleep(3)

        # we add this test because, maybe we are not on "Encounter Map" anymore
        # (like after the final boss)
        elif find_element(UIElement.view_party.filename, Action.screenshot):
            search_battle_list = []
            battletypes = ["protector", "fighter", "caster"]
            # random.shuffle(battletypes)
            boontypes = ["boonfighter", "boonprotector", "booncaster"]
            # random.shuffle(boontypes)
            encountertypes = battletypes + boontypes
            battletypes.append("elite")
            encountertypes.append("elite")
            for encounter in encountertypes:
                tag = f"encounter_{encounter}"
                coords = find_element(
                    getattr(UIElement, tag).filename, Action.get_coords
                )
                if coords:
                    battlepreference = f"prefer{encounter}"
                    x = coords[0]
                    y = (
                        coords[1] + (windowMP()[3] // 10.8)
                        if encounter in battletypes
                        else coords[1]
                    )

                    if settings_dict[battlepreference]:
                        search_battle_list.insert(0, (x, y))
                    else:
                        search_battle_list.append((x, y))
            if search_battle_list:
                log.info(f"{search_battle_list=}")
                x, y = search_battle_list.pop(0)
                mouse_click("right")
                move_mouse_and_click(windowMP(), x, y)
                rsleep(2)
            else:
                searchForEncounter()

        else:
            defaultCase()

    return retour


def searchForEncounter():
    """
    Search for the next encounter on the map.
    """
    retour = True
    if find_element(UIElement.view_party.filename, Action.screenshot):
        x, y = mouse_position(windowMP())
        log.debug("Mouse (x, y) : (%s, %s)", x, y)
        if y >= (windowMP()[3] // 2.2 - MOUSE_RANGE) and y <= (
            windowMP()[3] // 2.2 + MOUSE_RANGE
        ):
            x += windowMP()[2] // 25
        else:
            x = windowMP()[2] // 3.7

        if x > windowMP()[2] // 1.5:
            log.debug("Didnt find a battle. Try to go 'back'")
            find_element(Button.back.filename, Action.move_and_click)
            retour = False
        else:
            y = windowMP()[3] // 2.2
            log.debug("move mouse to (x, y) : (%s, %s)", x, y)
            move_mouse_and_click(windowMP(), x, y)
    return retour


def check_boss_battle():
    if settings_dict["stopatbossfight"] is True and find_element(
        UIElement.boss.filename, Action.screenshot
    ):
        send_notification({"message": "Stopping before Boss battle."})
        send_slack_notification(
            json.dumps({"text": "@channel Stopping before Boss battle."})
        )
        log.info("Stopping before Boss battle.")
        sys.exit()

    if settings_dict["quitbeforebossfight"] is True and find_element(
        UIElement.boss.filename, Action.screenshot
    ):
        rsleep(1)
        return quitBounty()

    return False


def handle_win():
    """
        Handles the actions to be performed when the battle is won.

        Returns:
            bool: True if the battle was won and rewards were collected, False otherwise.
    """
    log.info("goToEncounter : Battle won")
    while True:
        if not find_element(UIElement.take_grey.filename, Action.screenshot):
            mouse_click()
            rsleep(0.5)
        else:
            chooseTreasure()
            break

        if not find_element(UIElement.replace_grey.filename, Action.screenshot):
            mouse_click()
            rsleep(0.5)
        else:
            chooseTreasure()
            break

        if find_element(UIElement.reward_chest.filename, Action.screenshot):
            send_notification({"message": "Boss defeated. Time for REWARDS !!!"})
            send_slack_notification(
                json.dumps({"text": "Boss defeated. Time for REWARDS !!!"})
            )
            log.info("goToEncounter : " "Boss defeated. Time for REWARDS !!!")
            collect()
            return True
    move_mouse(windowMP(), windowMP()[2] / 10, windowMP()[3] / 2)
    return False


def handle_lose():
    """
        Handles the actions to be performed when the battle is lost.

        Returns:
            bool: Always returns True.
    """
    send_notification({"message": "goToEncounter : Battle lost"})
    send_slack_notification(json.dumps({"text": "goToEncounter : Battle lost"}))
    log.info("goToEncounter : Battle lost")
    return True


def handle_unknown():
    """
        Handles the actions to be performed when it's unknown what happened in the battle.

        Returns:
            bool: Always returns True.
    """
    log.info("goToEncounter : don't know what happened !")
    return True


def goToEncounter():
    """
    Start new fight,
    continue on the road and collect everything (treasure, rewards, ...)
    """
    log.info("goToEncounter : entering")
    rsleep(2)
    travelEnd = False

    fight_count = 0

    step_count = 0
    while not travelEnd:
        # TODO: infinite loop if the game is stuck
        if find_element(Button.play.filename, Action.screenshot):
            if settings_dict["max_fights"] != 0 and fight_count >= settings_dict["max_fights"]:
                rsleep(1)
                quitBounty()
                break                
            travelEnd = check_boss_battle()
            if travelEnd:
                break

            while find_element(Button.play.filename, Action.move_and_click):
                rsleep(1)

            retour = selectCardsInHand()
            log.info("goToEncounter - retour = %s", retour)
            rsleep(1)

            if retour == "win":
                travelEnd = handle_win()
            elif retour == "lose":
                travelEnd = handle_lose()
            else:
                travelEnd = handle_unknown()

            fight_count += 1
        else:
            if not nextlvl():
                break
            else:
                step_count += 1
                if step_count > 30:
                    break

    for x in range(60):
        if not find_element(UIElement.bounties.filename, Action.screenshot):
            look_at_campfire_completed_tasks()
            move_mouse_and_click(windowMP(), windowMP()[2] / 2, windowMP()[3] / 1.25)
            rsleep(2)

    if not find_element(UIElement.bounties.filename, Action.screenshot):
        defaultCase()
        rsleep(2)


def travelToLevel(page="next"):
    """
    Go to a Travel Point, choose a level/bounty and go on the road to make encounter
    """

    retour = False

    if find_element(
        f"levels/{settings_dict['location']}"
        f"_{settings_dict['mode']}_{settings_dict['level']}.png",
        Action.move_and_click,
        jthreshold["levels"],
    ):
        wait_until_timeout(Button.choose_level, 6)
        find_element(Button.choose_level.filename, Action.move_and_click)
        send_slack_notification(
            json.dumps({"text": "Starting %s bounty." % settings_dict["location"]})
        )
        rsleep(0.3)
        retour = True
    elif page == "next":
        if find_element(Button.arrow_next.filename, Action.move_and_click):
            rsleep(1)
            retour = travelToLevel("next")
        if retour is False and find_element(
            Button.arrow_prev.filename, Action.move_and_click
        ):
            rsleep(1)
            retour = travelToLevel("previous")
        elif retour is False:
            find_element(Button.back.filename, Action.move_and_click)
    elif page == "previous":
        if find_element(Button.arrow_prev.filename, Action.move_and_click):
            rsleep(1)
            retour = travelToLevel("previous")
        else:
            find_element(Button.back.filename, Action.move_and_click)
    return retour


def selectGroup():
    """Look for the mercenaries group 'Botwork' and select it
    (click on 'LockIn' if necessary)"""

    log.debug("selectGroup : entering")

    group = settings_dict.get("group", 1)
    group -= 1

    # group position is 3*3 grid
    # x from 430 to 978 of 1920
    # y from 340 to 658 of 1080
    window_width = windowMP()[2]
    window_height = windowMP()[3]
    width_ratio = window_width / 1920
    height_ratio = window_height / 1080
    x_start = 430 * width_ratio
    y_start = 340 * height_ratio
    x_offset = (978 - 430) / 2 * width_ratio
    y_offset = (658 - 340) / 2 * height_ratio
    group_x = x_start + x_offset * (group % 3)
    group_y = y_start + y_offset * (group // 3)
    

    # bad code but easily works
    # need to change it later to have a better solution

    if find_element(UIElement.choose_party.filename, Action.get_coords):
        move_mouse_and_click(windowMP(), group_x, group_y)
        rsleep(0.2)
        mouse_click()
        find_element(Button.choose_team.filename, Action.move_and_click)
        move_mouse(windowMP(), windowMP()[2] / 1.5, windowMP()[3] / 2)
        wait_until_timeout(Button.lockin, 3)
        for _ in range(3):
            if not find_element(Button.lockin.filename, Action.move_and_click):
                break
            rsleep(0.2)
    log.debug("selectGroup : ended")
    return
