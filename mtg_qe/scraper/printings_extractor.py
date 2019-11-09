# Samuel Dunn
# CS483, F19

import re
import sys

class PrintingExtractor(object):
    def __init__(self, link, page_soup):
        self._link = link
        self._page_soup = page_soup

    def extract_printing_information(self):
        """
        Finds all sets with this card printed in it, returns a dictionary
        keyed by the set names, where values are the multiverse id of the printing.
        """
        # there are two tables on the page with the class='cardList', the first
        # contains entries of other printings
        # the latter contains format legality.
        tables = self._page_soup.find_all('table', class_='cardList')
        if len(tables) != 2:
            raise RuntimeError(f"Card's format page is unrecognized! (page={self._link})")

        # For each row in the table, we want the 'Card Name' column, and the 'Set' column.
        # the 'Card Name:' column will contain a link to the card's detail page, which we can extract
        # the multiverseid from.
        card_names = self._extract_all_col_values(tables[0], 'Card Name:', True)
        sets = self._extract_all_col_values(tables[0], 'Set')

        if len(card_names) != len(sets):
            # We'd be up a creek if this error occurs.
            raise RuntimeError("??? ??? ???")

        ret = {}
        for x in range(len(card_names)):
            link = card_names[x].find('a')
            if link == -1:
                print(f"card_names[x]: {str(card_names[x].prettify())}", file=sys.stderr)
            mid = re.match(r'.*[\?\&]multiverseid=(\d*).*', card_names[x].find('a')['href']).group(1)
            ret[sets[x]] = mid

        return ret

    def extract_format_information(self):
        """
        Finds the format legality information on the page, returns legal formats by name as a list.
        """
        tables = self._page_soup.find_all('table', class_='cardList')
        if len(tables) != 2:
            raise RuntimeError(f"Card's format page is unrecognized! (page={self._link})")

        formats = self._extract_all_col_values(tables[1], 'Format')
        legality = self._extract_all_col_values(tables[1], 'Legality')
        legal_formats = [x[0] for x in zip(formats, legality) if x[1].lower() == 'legal']

        return legal_formats

    def _extract_all_col_values(self, table, col_header, leave_as_parse_node=False):
        c = 0
        header = table.find('tr', class_='headerRow')
        for col in header.children:
            span = col.find('span')
            if span and span != -1 and span.getText().strip() == col_header:
                break
            c += 1

        # now we know which column to pull values from in the non-header rows.
        l = []
        for row in table.find_all('tr', class_='cardItem'):
            children = [x for x in row.children] # the row.children property is an iterable, but not subscriptable (which is what we need)
            if len(children) <= c:
                # This occurs when there's no relevant information for this card.
                # EX: the card has no legal play formats.
                self._log.warn(f"Unable to find '{col_header}'' info for this card.")
                return []

            if leave_as_parse_node:
                l.append(children[c])
            else:
                l.append(children[c].getText().strip())

        return l