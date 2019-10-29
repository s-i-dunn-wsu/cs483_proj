# Samuel Dunn
# CS 483 Fall2019

from enum import Enum, auto
from requests.compat import urljoin

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
    def __init__(self, link, page_soup, multiverseid):
        self._link = link
        self._multiverseid = multiverseid
        self._page_soup = page_soup
        self._soup = page_soup.find('td', 'rightCol')

        # Figure out our content IDs.
        # Pages will typically have a JS section wherein it defines all
        # the IDs (function ClientIDs() {}; ClientIDs.nameRow='...' kind
        # of stuff.)

    def extract(self):
        """
        Extracts the card information from the card's page and
        returns an instance of mtg_qe.model.card.Card.
        """
        def extract_text(id, may_be_empty=True):
            try:
                return self._soup.find('div', id=id).find('div', class_='value').getText().strip()
            except Exception:
                if may_be_empty:
                    pass
                else:
                    raise

        card = Card()

        card.gatherer_link = self._link
        card.multiverseid = self._multiverseid
        card.external_artwork = self._page_soup.find('img', id='ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_cardImage')['src']
        card.name = extract_text(ContentRowIds.Name, False)
        card.type = extract_text(ContentRowIds.Type, False)

        if not 'land' in card.type.lower():
            card.mana_cost = extract_text(ContentRowIds.Mana) # Card handles converting to Mana objects.

        if 'creature' in card.type.lower():
            card.set_pt(extract_text(ContentRowIds.PT))

        card.text = extract_text(ContentRowIds.Text)
        card.flavor = extract_text(ContentRowIds.Flavor)
        card.rarity = extract_text(ContentRowIds.Rarity, False)
        card.expansion = extract_text(ContentRowIds.Expac, False)
        card.set_number = extract_text(ContentRowIds.Number)

        return card