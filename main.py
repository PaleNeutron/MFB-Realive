#! /usr/bin/env python3
"""
Main script. This tries to find your game window and launch for you
"""
import logging
import sys
import time

from modules.battlenetloop import enter_from_battlenet
from modules.gameloop import where
from modules.platforms import win
from modules.reconnects import game_closed
from modules.resolution import gen_images_new_resolution
from modules.utils import rsleep

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def main():
    """
    Checks python and tries to find the Hearthstone or Battle.net window.
    """
    log.info("Python version: %s", sys.version)
    gen_images_new_resolution()
    # Sometimes it is the first BN window shall be launched, sometimes it is the second.
    BNCount = 1
    idle_count = 0
    while True:
        log.debug("Loop")
        try:
            if win.find_game("Hearthstone"):
                BNCount = 1
                success = where()
                if success:
                    idle_count = 0
                else:
                    idle_count += 1
                    if idle_count > 20:
                        log.info("Idle for 10 loops, kill Hearthstone")
                        game_closed()
            elif win.find_game("Battle.net", BNCount):
                enter_from_battlenet()
                if BNCount == 0:
                    BNCount = 1
                else:
                    BNCount = 0
            else:
                rsleep(1)
        except KeyboardInterrupt as kerr:
            log.info("Keyboard Interrupt %s", kerr)
            sys.exit(0)
        except Exception as error:
            log.exception("Error: %s", error)
            rsleep(1)


if __name__ == "__main__":
    main()
