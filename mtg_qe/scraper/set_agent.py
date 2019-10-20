# Samuel Dunn
# CS 483, Fall 2019

import re
from bs4 import BeautifulSoup as bs
from requests.compat import urljoin
import logging

try:
    from .agent import Agent
    from .card_extractor import CardExtractor
except ImportError:
    from mtg_qe.scraper.agent import Agent
    from mtg_qe.scraper.card_extractor import CardExtractor

class SetAgent(Agent):
    def _prep_for_task(self, set_name, regulator):
        """
        Preps this agent for fetching cards from the set
        specified by `set_name`

        :param str set_name: The name of the set this task represents.
        :param RequestRegulator regulator: the request regulator to use
            while performing this task.
        """
        self._acitve_set_name = set_name
        self._active_regulator = regulator
        self._current_page = 0

        self._log = logging.getLogger("SetAgent").getChild(set_name)

        self._log.info(f"Agent prepping to work on set: {self._acitve_set_name}")

        # Fetch the set's page from gatherer.
        # I'd prefer to use requests.get's params keyword arg to format
        # the URL, but gatherer seems to expect brackets around the set names (presumably
        # for multiple sets to be searched over), and I haven't figured out how to get
        # requests to mimic that, yet. (Need to beware of some characters... "'"-> %27, etc.)
        search_url = self.__get_search_page_href(set_name)
        body = self._active_regulator.get(self.__get_search_page_href(set_name))
        soup = bs(body, features='html.parser')

        # Determine the total number of pages involved
        nav_bar = soup.find('div', id="ctl00_ctl00_ctl00_MainContent_SubContent_topPagingControlsContainer")
        if nav_bar:
            # k, so this is kinda janky.
            # The nav_bar will contain a list of <a> links to other pages of the same search
            # but if, for some reason, there are more than ~15 pages (may vary a bit)
            # then the last link will be '>>' and its href will be to the last page in the
            # returned set of cards.

            # So, what we need to do:
            # - check if there's the '>>' link, if so extract the page parameter from its url.
            #       set that as the 'max page' value
            # - if there is no '>>' link, attempt to find the highest page amongst links (should be
            #   index -2, as the last index will be the '>' next page link.)

            # The other option is that we could find and extract teh 'total found'
            # value (in the header, surrounded by parenthesis)
            # as there is 100 cards per page, we could calculate total pages
            # and proceed from there. I'm wary of this as it depends on
            # the site maintaining 100 cards max per page.
            a_links = nav_bar.find_all('a')
            if len(a_links) == 0:
                # there's only this page.
                self._max_page = 0

            else:
                if a_links[-1].getText() == '>>':
                    # NOTE: I'm also wary of this comparison, if for whatever reason
                    #       some pages are using unicode '>'s and others arent, it'd break.
                    #       works on the pages I've tested though.
                    max_link = a_links[-1]
                else:
                    max_link = a_links[-2]

                # Extract the max_page value from the link's url.
                self._max_page = int(re.match(r'.*[\?\&]page=(\d*).*', max_link['href']).group(1))

        # Get the list of cards on the first page:
        self._cards_on_page = self.__extract_card_links_from_page(soup, search_url)

        self._log.debug(f"\tFound: {self._max_page} pages worth of items (~{self._max_page * 100} to {((self._max_page + 1) * 100) - 1} cards)")
        self._log.debug(f"\tFound {len(self._cards_on_page)} cards on the first page.")
        # Aaand we're done for now
        # we'll have to have a compound iteration occurring in _next to
        # allow it to know when to get the next page's worth of content.

    def _generate_items(self):
        """
        """
        # need to iterate over all cards on the page
        # and all pages <= max_page.
        while self._current_page <= self._max_page:
            for link in self._cards_on_page:
                yield self.__extract_card_from_link(link)

            self._current_page += 1
            if self._current_page <= self._max_page:
                # Fetch the new page, update list of card links
                search_url = self.__get_search_page_href(self._acitve_set_name, self._current_page)
                soup = bs(self._active_regulator.get(search_url), features='html.parser')
                self._cards_on_page = self.__extract_card_links_from_page(soup, search_url)

    def __extract_card_links_from_page(self, page_soup, base_link):
        """
        Finds all links to cards in a page's results table.
        returns a list of those links. (normalized to the domain)
        """
        # all cards are located in a table, class = 'cardItemTable'.
        # each card is, itself, a sub-table. Each of these sub tables has a
        # <a> link with an id that ends with 'cardTitle'.

        cardTable = page_soup.find("table", "cardItemTable")
        ret = []
        for link in cardTable.find_all('a'):
            try:
                link['id']
            except KeyError:
                continue

            if link['id'].endswith('cardTitle'):
                ret.append(urljoin(base_link, link['href']))

        return ret

    def __get_search_page_href(self, set_name, page=0):
        return f"/Pages/Search/Default.aspx?page={page}&set=[\"{self._acitve_set_name.replace(' ', '+')}\"]"

    def __extract_card_from_link(self, link):
        # Get the page
        self._log.info(f"Extracting from link: {link}")
        card_page = bs(self._active_regulator.get(link), features='html.parser')

        # Pass over to a card extractor to finish fetching.
        return CardExtractor(link, card_page).extract()