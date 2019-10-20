# Samuel Dunn
# CS 483 Fall2019

from enum import Enum, auto

try:
    from ..model.card import Card
except ImportError:
    from mtg_qe.model.card import Card

class ManaTypes(Enum):
    Red = auto()
    Black = auto()
    Green = auto()
    Blue = auto()
    White = auto()
    Colorless = auto()

class ContentRowIds:
    Name = "ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_nameRow"
    Mana = "ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_manaRow"
    CMC  = "ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_cmcRow"
    Type = "ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_typeRow"    # May also contain race/tribe info.
    PT   = "ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_ptRow"  # The power / toughness of the creature.
    Text = "ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_textRow"
    Expac = "ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_setRow"
    Flavor = "ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_flavorRow"
    Rarity = "ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_rarityRow"
    Number = "ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_numberRow"
    Artist = "ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_artistRow"

class CardExtractor(object):
    """
    This class manages taking a beautiful soup object of a card's page
    and converting it into a mtg_qe.model.card.Card instance.
    """
    def __init__(self, link, page_soup):
        self._link = link
        self._page_soup = page_soup
        self._soup = page_soup.find('td', 'rightCol')

    def extract(self):
        """
        Extracts the card information from the card's page and
        returns an instance of mtg_qe.model.card.Card.
        """
        extract_text = lambda id: self._soup.find('div', id=id).find('div', class_='value').getText().strip()
        card = Card()

        card.name = extract_text(ContentRowIds.Name)
        card.type = extract_text(ContentRowIds.Type)

        if not 'land' in card.type.lower():
            card.mana_cost = extract_text(ContentRowIds.Mana) # Card handles converting to Mana objects.

        if 'creature' in card.type.lower():
            card.set_pt(extract_text(ContentRowIds.PT))

        try:
            card.text = extract_text(ContentRowIds.Text)
        except AttributeError:
            pass # no rules text

        try:
            card.flavor = extract_text(ContentRowIds.Flavor)
        except AttributeError:
            pass # no flavor text.

        card.rarity = extract_text(ContentRowIds.Rarity)

        expac = extract_text(ContentRowIds.Expac)
        card.add_expac(expac)

        try:
            card.add_set_number(expac, extract_text(ContentRowIds.Number))
        except AttributeError:
            # No set number.
            pass

        card.add_link(self._link)

        return card