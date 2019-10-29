# Samuel Dunn
# CS483, F19
# This module provides classes to help the project interface with json (custom encoders and decoders.)

import json
from ..model.card import Card

class CardEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Card):
            return obj.serialize()
        # if its not a card, treat it normally
        return json.JSONEncoder.default(self, obj)
