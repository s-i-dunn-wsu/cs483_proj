# Samuel Dunn
# CS 483, Fall 2019

class SearchResults(object):
    """
    There are two scenarios we'll find ourselves in when getting
    results from whoosh, when we can rely solely on whoosh and when
    we need to do pre-processing (this boils down to point query or no point query).

    In the former this class behaves merely as a shell to the whoosh results page.

    In the latter case we need to filter whoosh's results ourselves.

    Either way, this class serves to facilitate the representation of result
    data.
    """
    def __init__(self, search_type, query_params, searcher = None):
        """
        """
        self._searcher = searcher

    def close(self):
        """
        Closes the searcher object, if applicable.
        """
        if self._searcher:
            self._searcher.close()

    def get_page(self, n, page_size = 10):
        """
        returns the n'th page in the result set
        """