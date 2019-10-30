# Samuel Dunn
# CS483, F19
# This file provides functions and other helpers for interacting with custom paths

import re
import urllib

def normalize_name(name):
    """
    Returns a new string that can be used as a consistent, space free,
    equivalent to name, can be used for sets or cards.
    :param str name: the name of a set.
    :return: a normalized, path-safe, equivalent.
    """
    return re.sub(r'\s+|\\|/|\[|\]', '_', name)

def join_urls(base, url):
    """
    Joins the components of a url the same way urllib would
    but is parameter-wary (that is, it won't convert special characters like & to their escaped equivalents)
    """
    a = urllib.parse.urlparse(base)
    b = urllib.parse.urlparse(url)

    # now join the two path components and tack b's query parameters back on
    ret = urllib.parse.urljoin(a.path, b.path)
    if b.query:
        ret += '?' + b.query

    return ret