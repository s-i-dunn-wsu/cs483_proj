# Samuel Dunn, Noah Scarbrough
# CS 483, F19

# This module defines an MTG card class.
# For reference:
# https://mtg.gamepedia.com/Parts_of_a_card
# https://magic.wizards.com/en/articles/archive/magic-academy/anatomy-magic-card-2006-10-21

import os
from requests.compat import urljoin

try:
    from ..utils.path_helpers import normalize_name, join_urls
except ImportError:
    from mtg_qe.utils.path_helpers import normalize_name, join_urls

class Card(object):
    def __init__(self):
        self._artist = None
        self._name = None
        self._mana = None
        self._cmc = None
        self._type = None
        self._subtypes = None
        self._rarity = None
        self._expansion = None
        self._set_number = None
        self._rules_text = None
        self._flavor_text = None
        self._pt = None
        self._printings = []
        self._legal_in = []
        self._external_link = None
        self._external_img_link = None

    def serialize(self):
        """
        Called when being converted to json for long term storage.
        MUST return a json serializable object.

        .. note::
            whatever format this method returns is what will be passed back to
            calls to deserialize, therefore it may be useful to include a schema
            version, allowing us to ensure backwards compatibility.
        """
        return {
            "schema": 1,
            "name": self.name,
            "rarity": self.rarity,
            "mana": self.mana_cost,
            "cmc": self.cmc,
            "type": self.type,
            "subtypes": self.subtypes,
            "text": self.text,
            "flavor_text": self.flavor,
            "power": self.power,
            "toughness" : self.toughness,
            "expansion": self.expansion,
            "printings": self.other_prints,
            "set_number": self.set_number,
            "formats" : self.legal_formats,
            "artwork_external" : self.external_artwork,
            "artwork_internal" : self.local_artwork,
            "multiverseid": self.multiverseid
        }

    @property
    def multiverseid(self):
        """
        indicates the card's multiverse id.
        """
        return self._multiverseid

    @multiverseid.setter
    def multiverseid(self, value):
        """
        """
        self._multiverseid = int(value)

    @property
    def name(self):
        """
        Returns the cards name as it is on the card. (case sensitive)
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        Sets the cards name to value
        """
        self._name = value

    @property
    def mana_cost(self):
        """
        Returns the ManaCost of a card.
        """
        return None if self._mana is None else tuple(self._mana)

    @mana_cost.setter
    def mana_cost(self, value):
        """
        Sets the mana cost of the card (convert to the appropriate class as necessaary)
        """
        self._mana = value[:]

    @property
    def cmc(self):
        """
        Returns the converted mana cost of the card.
        """
        if not self.mana_cost:
            return 0

        if self._cmc is None:
            l = []
            for x in self.mana_cost:
                try:
                    l.append(int(x))
                except Exception:
                    l.append(1)

            self._cmc = sum(l)

        return self._cmc

    # no setter for cmc, its calculated from mana_cost

    @property
    def type(self):
        """
        Returns the cards type (creature, instant, sorc, etc.)
        """
        return self._type

    @type.setter
    def type(self, value):
        """
        Sets the cards type (ensure its a valid type)
        """
        # value will be <type(s)> [\u2014 <subtypes>]
        split = value.split('\u2014')
        self._type = split[0].strip()
        if len(split) > 1:
            self._subtypes = split[1].strip()

    @property
    def subtypes(self):
        """
        Returns the cards subtypes, if any.
        None otherwise.
        """
        return self._subtypes

    @property
    def text(self):
        """
        Returns the text on the card. (the most common 'doc' of a card.)
        """
        return self._rules_text

    @text.setter
    def text(self, value):
        """
        Sets the cards text
        """
        self._rules_text = value

    @property
    def flavor(self):
        """
        Returns this cards flavor text.
        """
        return self._flavor_text

    @flavor.setter
    def flavor(self, value):
        """
        Sets the cards flavor text
        """
        self._flavor_text = value

    @property
    def power(self):
        """
        If this card is a creature, return its power.
        """
        # can't convert to int, may be '*'
        if self._pt:
            return self._pt.split('/')[0].strip()

    @property
    def toughness(self):
        """
        If this card is a creature, return its toughness.
        """
        if self._pt:
            return self._pt.split('/')[1].strip()

    @property
    def p_t(self):
        """
        """
        return self._pt

    @p_t.setter
    def p_t(self, value):
        """
        """
        self._pt = value


    @property
    def rarity(self):
        """
        """
        return self._rarity

    @rarity.setter
    def rarity(self, value):
        """
        """
        self._rarity = value

    @property
    def expansion(self):
        """
        Returns the name of the expansion this card was scraped from.
        """
        return self._expansion

    @expansion.setter
    def expansion(self, value):
        if self._expansion is None:
            self._expansion = value
            self._printings.append(value)

    @property
    def set_number(self):
        """
        Returns the set number, or the card's number within this set, for this card.
        """
        return self._set_number

    @set_number.setter
    def set_number(self, value):
        if value is not None:
            # Not all Set Numbers are purely integers.
            self._set_number = value

    @property
    def other_prints(self):
        """
        Returns a list of expansions, by name, that also feature this card.
        """
        return tuple(self._printings)

    @other_prints.setter
    def other_prints(self, value):
        self._printings = value[:]

    @property
    def artwork_folder(self):
        """
        Returns an un-rooted path that can be used to locate the artwork information for this card.
        """
        return os.path.join('artwork', str(self._multiverseid))

    @property
    def local_artwork(self):
        """
        Returns an un-rooted path to where the artwork for this card should be saved.
        """
        return os.path.join('artwork', str(self._multiverseid), normalize_name(self._expansion) + '.png')

    @property
    def artist(self):
        return self._artist

    @artist.setter
    def artist(self, value):
        self._artist = value

    @property
    def external_artwork(self):
        """
        Returns a gatherer.wizards.com href to the card's artwork.
        """
        return self._external_img_link

    @external_artwork.setter
    def external_artwork(self, link):
        """
        """
        # ensure the artwork is not relative to some other link.
        if link.startswith('..'):
            if self._external_link:
                # we can join the two ourselves.
                self._external_img_link = join_urls(self._external_link, link)
            else:
                raise ValueError(f"Given relative link! ({link})")

        else:
            self._external_img_link = link

    @property
    def legal_formats(self):
        return tuple(self._legal_in)

    @legal_formats.setter
    def legal_formats(self, value):
        self._legal_in = value[:]

    @property
    def gatherer_link(self):
        """
        returns the link to gatherer for this particular printing.
        """
        return self._external_link

    @gatherer_link.setter
    def gatherer_link(self, link):
        """
        """
        self._external_link = link