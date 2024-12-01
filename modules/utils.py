"""
This module provides a function for updating dictionaries with new values.
"""

import random
import time
from copy import deepcopy


def update(base_dictionary, updated_dictionary):
    """Return dictionary updated with values u

    Args:
        d (dict): base dictionary to start with
        u (dict): dictionary with new values

    Returns:
        dict: dictionary with updated values
    """
    copied_dictionary = deepcopy(base_dictionary)
    for updated_k, updated_v in updated_dictionary.items():
        if isinstance(updated_v, dict):
            copied_dictionary[updated_k] = update(
                copied_dictionary.get(updated_k, {}), updated_v
            )
        elif updated_k in updated_dictionary:
            copied_dictionary[updated_k] = updated_dictionary[updated_k]

    return copied_dictionary


def rsleep(seconds):
    """Sleep for a specified number of seconds randomly chosen between 0.9 and 1.1 times the input value.

    Args:
        seconds (int): number of seconds to sleep
    """
    time.sleep(seconds * random.uniform(0.9, 1.1))