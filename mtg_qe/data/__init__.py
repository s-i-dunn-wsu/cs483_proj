# Samuel Dunn
# CS 483, Fall 2019

# This module is responsible for setting up the Whoosh! index
# and making an internal composite index (to aid in navigating cards
# with out relying on re-searching the whoosh index.)

# In addition to performing these set-up oriented functions, it
# serves as an API to the web server code to interface with
# these data sources.

from . import whoosh_integrations
from . import internal_index_integration

def get_index_location():
    """
    Locates the path to the indexes (both whoosh and basic)
    this may be different based on if the index was set up
    by a pip installation.
    """

def get_whoosh_index():
    """
    """
    return whoosh_integrations.get_index_object()

def simple_query(query, or_group=False, page = 0, n = 10):
    """
    Performs a simple keyword query using `query` through whoosh. This, by default, will look at all 3 major text based fields. (name, rules text, flavor text.)
    :param str query: the input query
    :param bool or_group: specifies whetehr to use a AND grouping or an OR grouping.
    :param int page: the page to return.
    :param int n: how many results should be in the return set.
    :return: Exact class TBD, will provide way to iterate over the page's worth of results.
    """

def advanced_query(text_parameters, range_parameters = {}, point_parameters = {}, page = 0, n = 10):
    """
    :param dict text_paramters: a dictionary of field-to-query pairs specifying text-based queries.
        this is good for fields like "rules_text", "name", "flavor_text", etc.
    :param dict range_parameters: a dictionary of field to range pairs.
        this is good for fields like power, toughness, cmc, etc.
    :param dict point_parameters: a dictionary of field to value parameters. Every card in the return
        set must have an exact match to every value in the dict.
        In example, if point_parameters is {'cmc': 5} then for every card in the set card.cmc == 5 must evaluate to true.
        .. warning::
            using this parameter will cause the query system to filter through whoosh results, slowing down computation.
    :param int page: the 'page' of results to return
    :param int n: the number of results per page.
    :return: Exact class TBD, will provide way to iterate over the page's worth of results.
    """

def get_internal_index():
    """
    """

def find_card_by_multiverseid(multiverseid):
    """
    """
    return get_internal_index().get(int(multiverseid), None)

def find_card_by_name(name):
    """
    """
    return get_internal_index().get(name, None)