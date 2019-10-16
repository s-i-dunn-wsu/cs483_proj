# Samuel Dunn, Noah Scarbrough
# CS 483, F19

# This module defines an MTG card class.
# For reference:
# https://mtg.gamepedia.com/Parts_of_a_card
# https://magic.wizards.com/en/articles/archive/magic-academy/anatomy-magic-card-2006-10-21

class Card(object):
    def __init__(self):
        pass

    @property
    def name(self):
        """
        Returns the cards name as it is on the card. (case sensitive)
        """
        pass

    @name.setter
    def name(self, value):
        """
        Sets the cards name to value
        """
        pass


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
        pass

    @type.setter
    def type(self, value):
        """
        Sets the cards type (ensure its a valid type)
        """
        pass

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
    def artworks(self):
        """
        Returns the artwork(s) this card has. (includes link to image, artist name.)
        """

    def add_artwork(self, artwork):
        """
        Adds the given artwork to the set of arworks available for this card.
        """