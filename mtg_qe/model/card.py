# Samuel Dunn, Noah Scarbrough
# CS 483, F19

# This module defines an MTG card class.
# For reference:
# https://mtg.gamepedia.com/Parts_of_a_card
# https://magic.wizards.com/en/articles/archive/magic-academy/anatomy-magic-card-2006-10-21

class Card(object):
    def __init__(self):
        self._name = None
        self._type = None

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
            "mana": self.mana_cost,
            "cmc": self.cmc,
            "mana_cost": self.mana_cost,
            "type": self.type,
            "subtypes": self.subtypes,
            "text": self.text,
            "flavor_text": self.flavor,
            "power": self.power,
            "toughness" : self.toughness,
            "expansions": self.expacs,
            "arts": self.artworks,
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
        pass

    @mana_cost.setter
    def mana_cost(self, value):
        """
        Sets the mana cost of the card (convert to the appropriate class as necessaary)
        """

    @property
    def cmc(self):
        """
        Returns the converted mana cost of the card.
        """

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
        self._type = value

    @property
    def subtypes(self):
        """
        Returns the cards subtypes, if any.
        None otherwise.
        """
        pass

    @property
    def text(self):
        """
        Returns the text on the card. (the most common 'doc' of a card.)
        """
        pass

    @text.setter
    def text(self, value):
        """
        Sets the cards text
        """
        pass

    @property
    def flavor(self):
        """
        Returns this cards flavor text.
        """
        pass

    @flavor.setter
    def flavor(self, value):
        """
        Sets the cards flavor text
        """

    @property
    def power(self):
        """
        If this card is a creature, return its power.
        """
        pass

    @power.setter
    def power(self, value):
        """
        Sets this cards power. (check to make sure its valid.)
        """
        pass

    @property
    def toughness(self):
        """
        If this card is a creature, return its toughness.
        """
        pass

    @toughness.setter
    def toughness(self, value):
        """
        """
        pass

    def set_pt(self, pt):
        """
        A quick way to set power and toughness, since
        they're usually given in one go.
        """
        self.power, self.toughness = pt.split('/')

    @property
    def rarity(self):
        """
        """

    @rarity.setter
    def rarity(self, value):
        """
        """

    @property
    def expacs(self):
        """
        Returns the expansion(s) the card is present in.
        """

    def add_expac(self, expansion):
        """
        Adds the given expansion to the list of expansions this card is present in.
        """

    @property
    def set_numbers(self):
        """
        Returns the expansion : set number associations.
        """

    def add_set_number(self, expac, number):
        """
        """

    @property
    def artworks(self):
        """
        Returns the artwork(s) this card has. (includes link to image, artist name.)
        """

    def add_artwork(self, expac, artwork):
        """
        Adds the given artwork to the set of arworks available for this card.
        """

    @property
    def gatherer_links(self):
        """
        Indicates the pages where this card was located
        on gatherer.wizards.com
        """

    def add_link(self, link):
        pass