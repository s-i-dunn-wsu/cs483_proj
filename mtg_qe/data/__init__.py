# Samuel Dunn
# CS 483, Fall 2019

# This module is responsible for setting up the Whoosh! index
# and making an internal composite index (to aid in navigating cards
# with out relying on re-searching the whoosh index.)

# In addition to performing these set-up oriented functions, it
# serves as an API to the web server code to interface with
# these data sources.

def get_index_location():
    """
    Locates the path to the indexes (both whoosh and basic)
    this may be different based on if the index was set up
    by a pip installation.
    """

def get_whoosh_index():
    """
    """

def perform_whoosh_simple_query(query, or_group=False):
    """
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