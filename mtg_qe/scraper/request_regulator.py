# Samuel Dunn
# CS 483, Fall 2019

import logging
import re
import requests
import time
from requests.compat import urljoin

class RequestRegulator(object):
    """
    This class manages respecting a domain's robot policy and regulates requests to a given domain.
    """
    def __init__(self, domain):
        if '://' not in domain:
            domain = "https://" + domain
        self._domain = domain
        self._last_request_time = 0
        self._log = logging.getLogger('Requester').getChild(domain)

        self._load_robots_policies()

    def get_url_for(self, href):
        """
        Creates and returns an appropriate, full, url for the given href.
        :param str href: the href to build a url out of.
        :return: a string url
        """
        # Correct the href if it already has this domain in it.
        href = href.replace(self._domain, '')
        return urljoin(self._domain, href)

    def get(self, href, as_bytes = False, as_json = False, **kwargs):
        """
        :param str href: the extension to get the url from.
        :param bool as_json: will parse the requested data as json and return the deserialized object.
        :param bool as_bytes: returns the un-encoded version of the requests response.
        :param kwargs: keyword arguments to pass to requests.get
        :return: The body of the page at the indicated href, None if unable to safely get the page (200 status code), or hte page was disallowed
        """
        href = href.replace(self._domain, '')

        if href in self._disallowed:
            return None

        url = urljoin(self._domain, href)

        # TODO: if ever multithreading this will need to be made thraed-safe
        # Ensure we're not violating the chrawl delay:
        if time.time() < self._delay_time + self._last_request_time:
            time.sleep((self._delay_time + self._last_request_time) - time.time())

        r = requests.get(url, **kwargs)
        self._last_request_time = time.time()

        if r.status_code in range(200, 300):
            if as_bytes:
                return r.content
            if as_json:
                return r.json()
            else:
                return r.text

        else: return None

    def _set_default_policies(self):
        """
        """
        self._delay_time = 1
        self._disallowed = tuple()

    def _load_robots_policies(self):
        """
        """
        # Open self._domain/robots.txt
        # Load the data (adhere to any rules supplied to all agents.)
        # We're particularly interested in crawl delay.
        r = requests.get(urljoin(self._domain, 'robots.txt'))

        if r.status_code not in range(200, 300):
            # Set some defaults, and hope for the best.
            self._log.warn("Unable to find robots.txt file")
            self._set_default_policies()

        text = r.text.strip().replace("\n\n", "\n")   # You can never strip enough whitespace.

        # Split on 'User-agent', find the block with '*' (all agents)
        # then load the desired policies.
        agent_rules = ['User-agent' + x for x in text.split('User-agent')]

        # local vars to store results in, double as confirmation of acquiring rules.
        disallowed = []
        delay_time = None

        for agent_cluster in agent_rules:
            if not re.search(r"User-agent\s*?:\s*\*\s*$", agent_cluster, flags=re.MULTILINE):
                continue # Not interested in this cluster (its for bing, google, etc.)

            self._log.debug(f"Found agent cluster: {repr(agent_cluster)}")

            for line in agent_cluster.split('\n'):
                if not line.strip():
                    continue    # Omit blank lines

                try:
                    key, value = line.split(":", 1)
                except:
                    print(line)
                    raise
                key = key.strip()
                value = value.strip()

                if key.lower() == "disallow":
                    disallowed.append(value.strip())
                elif key.lower() == "crawl-delay":
                    delay_time = int(value.strip())

        if delay_time is None:
            self._log.warn("Did not find an applicable agent ruleset. Assuming defaults")
            self._set_default_policies()

        else:
            self._delay_time = delay_time
            self._disallowed = tuple(disallowed)
