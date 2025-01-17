# Samuel Dunn
# CS 483, Fall 2019

# This module is responsible for setting up the Whoosh! index
# and making an internal composite index (to aid in navigating cards
# with out relying on re-searching the whoosh index.)

# In addition to performing these set-up oriented functions, it
# serves as an API to the web server code to interface with
# these data sources.

import os
import functools

from . import whoosh_integrations
from . import internal_index_integration

from whoosh.qparser import MultifieldParser, QueryParser, AndGroup, OrGroup

def require_unpacked_archive(meth):
    """
    this method ensures that the corpus archive is unpacked and ready to go
    """
    @functools.wraps(meth)
    def wrapper(*args, **kwargs):
        unpack_archive() # this method exits early if its not needed.
        return meth(*args, **kwargs)

    return wrapper

def get_data_location():
    """
    Locates the path to where data is saved.
    """
    here = os.path.dirname(os.path.abspath(__file__)) # the directory this file is located in.
    return os.path.join(here, 'corpus_files')

@require_unpacked_archive
def get_whoosh_index():
    """
    """
    try:
        return whoosh_integrations.get_whoosh_index()
    except Exception:
        unpack_archive()
        return whoosh_integrations.get_whoosh_index()

@require_unpacked_archive
def get_internal_index():
    """
    Returns the 'internal index' for the project.
    The internal index is a pair of dicts that arrange
    card objects in easy-to-use outside of whoosh ways.
    The first dict, keyed by 'by_name', stores cards instances
    with a unique name. The second dict, keyed by 'by_multiverseid',
    stores all cards (all cards scraped) by their multiverseid.
    Between the two, any time we have a result from whoosh and need
    to navigate to another card or print, we should be covered.
    """
    return internal_index_integration.get_internal_index()

def get_all_formats():
    """
    Returns a alpabetized tuple of all playable formats as discovered while scraping
    """
    return tuple(get_internal_index()['formats'])

def get_all_sets():
    """
    Returns an alphabetized tuple of all expansions discovered while scraping.
    """
    return tuple(get_internal_index()['expansions'])

def get_all_card_types():
    """
    Returns an alphabetized tuple of all card types discovered while scraping
    """
    return tuple(get_internal_index()['types'])

def get_all_card_subtypes():
    """
    Returns an alphabetized tuple of all card sub types discovered while scraping
    """
    return tuple(get_internal_index()['subtypes'])

def simple_query(query, or_group=False, page = 0, n = 10):
    """
    Performs a simple keyword query using `query` through whoosh. This, by default, will look at all 3 major text based fields. (name, rules text, flavor text.)
    :param str query: the input query
    :param bool or_group: specifies whetehr to use a AND grouping or an OR grouping.
    :param int page: the page to return.
    :param int n: how many results should be in the return set.
    :return: Exact class TBD, will provide way to iterate over the page's worth of results.
    """
    ix = get_whoosh_index()

    # fix `page` and `n` (they may be string versions of ints)
    page = int(page)
    n = int(n)

    # parse against the main text fields (note: subtypes is here to help aid in "tribe" searches, and boost planeswalker results)
    qparser = MultifieldParser(['rules_text', 'name', 'flavor_text'], ix.schema, group = OrGroup if or_group else AndGroup)

    query = qparser.parse(query.lower()) # all text fields are lowered in whoosh, so do same here

    with ix.searcher() as searcher:
        # Quick note: whoosh expects pages to start with 1, so we'll take page+1
        results = searcher.search_page(query, page+1, pagelen=n)
        return [x['data_obj'] for x in results]


def advanced_query(parameters, page = 0, n = 10):
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
    import whoosh.fields
    from whoosh.query import And, Or
    schema = get_whoosh_index().schema

    # fix `page` and `n` (they may be string versions of ints)
    page = int(page)
    n = int(n)

    # After talking with Ben it sounds like we can do something to the effect
    # of taking multiple sub queries and perform unions and intersections on their
    # results
    # This is going to be the best way to get the desired results.

    # to start: build a list of all the query objects we'll be searching.
    query_objs = []
    for field, target in parameters.items():
        # Coerce potential numeric point queries to whoosh syntax.
        if isinstance(target, float):
            target = int(target+0.5)
        if isinstance(target, int):
            target = str(target)
            #target = f"{{{target-1} TO {target+1}}}"
            #target = target.replace("[ TO", "[TO").replace("TO ]", "TO]")

        # Coerce range queries to whoosh syntax, assume they're inclusive bounds.
        if isinstance(target, (list, tuple)):
            if len(target) != 2:
                raise ValueError(f"Unable to treat parameter as range query! ({target})")
            target = f"[{target[0] if target[0] != -1 else ''} TO {target[1] if target[1] != -1 else ''}]"

            # whoosh has issues if there's an open ended range with a space separating TO from the bracket:
            target = target.replace("[ TO", "[TO").replace("TO ]", "TO]")

        # the comma-separated KEYWORD fields have been giving us some issue
        # it seems that whoosh is a bit bi-polar when it comes to commas in these fields.
        # so we'll add two subqueries, one with a comma and one without.
        if field in schema and isinstance(schema[field], whoosh.fields.KEYWORD):
            # add the extra query object:
            subqueries = [QueryParser(field, schema).parse(target.lower()+','),
                          QueryParser(field, schema).parse(target.lower())]
            query_objs.append(Or(subqueries))

        else:
            query_objs.append(QueryParser(field, schema).parse(target.lower())) # again, lower capitalization on everything

    if not len(query_objs):
        return []

    # now build a nice big compound query:
    query = And(query_objs)
    with get_whoosh_index().searcher() as searcher:
        # run that query and return the appropriate results page.
        try:
            results = searcher.search_page(query, page+1, n)
        except Exception:
            print(repr(query))
            raise

        return [x['data_obj'] for x in results]

def find_card_by_multiverseid(multiverseid):
    """
    Returns the card with matching multiverseid, or None if no match.
    Note: card printings have a 1 to 1 relationship with multiverseid.
    """
    # Coming out of json all keys will be converted to strings (even if they went in as ints)
    return get_internal_index()['by_multiverseid'].get(str(multiverseid), None)

def find_card_by_name(name):
    """
    Returns the card with matching multiverseid, or None if no match.
    Note: card printings have a many to 1 relationship with name.
    """
    return get_internal_index()['by_name'].get(name, None)

def unpack_archive():
    """
    Unpacks the archive if necessary. This is used indirectly as a CLI entry point and by some local
    methods if necessary.
    This function also serves as a CLI entry point.

    Info:
    The archive contains a folder 'corpus_data' that looks something like this:
    corpus_data/
        artwork/
            <all artwork folders and files>

        whoosh_index/
            <whoosh index files>
        internal_index.json
    """
    import os
    import logging

    logger = logging.getLogger(__file__)
    if os.path.exists(get_data_location()):
        logger.debug("corpus already extracted.")

    else:
        import tarfile

        # Find the .tar.gz packaged in with the bundle.
        here = os.path.dirname(os.path.abspath(__file__)) # the directory this file is located in.
        targz_files = [os.path.join(here, x) for x in os.listdir(here) if x.endswith('.tar.gz')]
        if len(targz_files) == 0:
            error_msg = "Unable to find corpus archive file!"
            logger.warn(error_msg)
            raise RuntimeError(error_msg)

        if len(targz_files) > 1:
            error_msg = "Unable to distinguish archive file, there are too many archives here"
            logger.warn(error_msg)
            raise RuntimeError(error_msg)

        with tarfile.open(targz_files[0], 'r:gz') as archive:
            try:
                archive.extractall(here)
            except Exception:
                logging.error("Encountered error extracting archive? Is this installed to base python interpreter? If so use sudo.")
                raise
