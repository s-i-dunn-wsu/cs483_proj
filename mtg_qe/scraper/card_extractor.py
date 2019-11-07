# Samuel Dunn
# CS 483 Fall2019

import re
import os
import logging
from enum import Enum, auto
from requests.compat import urljoin
from bs4 import BeautifulSoup as bs

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

        try:
            card.name = extract_text(self.identify_id('nameRow'), False)
        except Exception:
            try:
                os.makedirs('errors')
            except OSError:
                pass
            logging.getLogger("CE").error(f"MID:{card.multiverseid}, found ID: {self.identify_id('nameRow')}, encountered error.")
            with open(os.path.join('errors', str(card.multiverseid) + '.html'), 'w') as fd:
                fd.write(str(self._page_soup))

            raise

        self._extract_image_href(card)
        self._extract_rules_text(card)
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

        card.flavor = extract_text(self.identify_id('flavorRow'))
        card.rarity = extract_text(self.identify_id('rarityRow'), False)
        card.expansion = extract_text(self.identify_id('setRow'), False)
        card.set_number = extract_text(self.identify_id('numberRow'))

        return card

    def _extract_rules_text(self, card):
        """
        Attempts to extract the rules text in a format-savvy way.
        Merely finding the node and calling the getText() method
        of the BeautifulSoup object was leading to poor formatting
        (missing line breaks, ignored mana costs, etc.)
        This method attempts to resolve that by ensuring line breaks
        are adhered to, and mana costs are converted to ascii.
            ex: <green mana symbol> becomes {G}, 4 colorless becomes {4}
        """
        # Get the parse node with the data we want.
        id = self.identify_id('textRow')
        try:
            field = self._soup.find('div', id=id).find('div', class_='value')
        except Exception:
            # We'll except here if there is no rules text field.
            return

        # Now, rather than call .getText() on it, we'll
        # convert it to a string and do a manual parse on it.
        # Each clause is in its own <div class='cardTextBox'> field
        # any nested mana costs are <img> tags, as usual.
        # For the mana costs we'll use regular expression substitution.
        pattern = r'<\s*img\s.*?alt="(.).*?>'

        text_blocks = []

        # For the record: this can be done in a single comprehension.
        # A very illegible comprehension ;)
        for subfield in field.find_all('div', class_='cardtextbox'):
            corrected = re.sub(pattern, r"{\1}", str(subfield))

            # Now we pass the corrected field back into BeautifulSoup
            # (so we can use it to strip out nonsense like styling)
            soup = bs(corrected, features='html.parser')
            text_blocks.append(soup.getText().strip())

        card.text = "\n".join(text_blocks)

    def _extract_image_href(self, card):
        """
        finds the image link within self._page_soup.
        Must be called after the card's name is fetched.
        """
        # Iterate through all <img> tags, looking for one
        # where the 'alt' field matches card.name.
        # Fall back to trying to identify the cardImage ID and finding that
        img_tags = self._page_soup.find_all('img')

        for img in img_tags:
            try:
                if img['alt'].strip().lower() == card.name.strip().lower():
                    card.external_artwork = img['src']
                    return
            except Exception:
                continue

        # if we got here then we need to rely on the fall back strat.
        card.external_artwork = self._page_soup.find('img', id=self.identify_id('cardImage'))['src']
