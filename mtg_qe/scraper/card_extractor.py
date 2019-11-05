# Samuel Dunn
# CS 483 Fall2019

import re
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

contentIdDefaults = {
    'nameRow' : ContentRowIds.Name,
    'manaRow' : ContentRowIds.Mana,
    'cmcRow'  : ContentRowIds.CMC,
    'typeRow' : ContentRowIds.Type,
    'ptRow'   : ContentRowIds.PT,
    'textRow' : ContentRowIds.Text,
    'setRow'  : ContentRowIds.Expac,
    'flavorRow': ContentRowIds.Flavor,
    'rarityRow': ContentRowIds.Rarity,
    'numberRow': ContentRowIds.Number,
    'artistRow': ContentRowIds.Artist,
    'cardImage': "ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_cardImage"
}

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
        self._content_name_id = re.search(r'ClientIDs.nameRow', str(page_soup))

    def identify_id(self, str_id):
        """
        Takes a common string and identifies the id string used to identify
        the target element within page_soup.
        :param str str_id: the common string for the target id.
        :rtype: str
        :return: the id string used for the desired element.

        example:
        identify_id('nameRow') will find the id:
        'ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_nameRow' on *most* pages.
        """
        rs = r'ClientIDs.{}\s*=\s*[\'"](.*)[\'"];*'.format(str_id)
        m = re.match(rs, str(self._page_soup))
        if m:
            return m.group(1).strip()
        else:
            return contentIdDefaults[str_id]

    def extract(self):
        """
        Extracts the card information from the card's page and
        returns an instance of mtg_qe.model.card.Card.
        """
        def extract_text(id, may_be_empty=True):
            try:
                return self._soup.find('div', id=id).find('div', class_='value').getText().strip()
            except Exception:
                if not may_be_empty:
                    raise

        def extract_mana(sub_soup):
            return [x['alt'] for x in sub_soup.children if not isinstance(x, str)]

        card = Card()

        card.gatherer_link = self._link
        card.multiverseid = self._multiverseid
        card.external_artwork = self._page_soup.find('img', id=self.identify_id('cardImage'))['src']
        card.name = extract_text(self.identify_id('nameRow'), False)
        card.type = extract_text(self.identify_id('typeRow'), False)

        if not 'land' in card.type.lower(): # No land has mana cost, AFAIK
            # Some cards still may not have a mana cost though
            # so we need to be careful here.
            try:
                card.mana_cost = extract_mana(self._page_soup.find('div', id=self.identify_id('manaRow')).find('div', class_='value'))
            except AttributeError:
                pass

        if 'creature' in card.type.lower():
            card.p_t = extract_text(self.identify_id('ptRow'))

        card.text = extract_text(self.identify_id('textRow'))
        card.flavor = extract_text(self.identify_id('flavorRow'))
        card.rarity = extract_text(self.identify_id('rarityRow'), False)
        card.expansion = extract_text(self.identify_id('setRow'), False)
        card.set_number = extract_text(self.identify_id('numberRow'))

        return card