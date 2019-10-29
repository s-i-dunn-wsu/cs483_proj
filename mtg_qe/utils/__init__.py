# Samuel Dunn
# CS 483, F19

# this module provides utilities used elsewhere to help
# adhere to DRY principles.

import json
import re
from ..model.card import Card

class CardEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Card):
            return obj.serialize()
        # if its not a card, treat it normally
        return json.JSONEncoder.default(self, obj)

def normalize_name(name):
    """
    Returns a new string that can be used as a consistent, space free,
    equivalent to name, can be used for sets or cards.
    :param str name: the name of a set.
    :return: a normalized, path-safe, equivalent.
    """
    return re.sub(r'\s+|\\|/|\[|\]', '_', name)
