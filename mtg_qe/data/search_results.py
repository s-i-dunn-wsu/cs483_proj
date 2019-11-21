# Samuel Dunn
# CS 483, Fall 2019

import time



class SearchDelegate(object):
    """
    There are two scenarios we'll find ourselves in when getting
    results from whoosh, when we can rely solely on whoosh and when
    we need to do pre-processing (this boils down to point query or no point query).

    In the former this class behaves merely as a shell to the whoosh results page.

    In the latter case we need to filter whoosh's results ourselves.

    Either way, this class serves to facilitate the representation of result
    data.
    """

    def __init__(self, query_obj, point_params = None):
        """
        """
        self._query = query_obj
        self._point_params = point_params
        self._spawn_time = time.time()
        self._searcher = None

    def close(self):
        """
        Closes the active searcher object, if it exists.
        """
        if self._searcher is not None:
            self._searcher.close()


    def num_pages(self):
        """
        Returns the number of pages in the result set.
        """

    def get_page(self, n, page_size = 10):
        """
        returns the n'th page in the result set
        """
        return self._do_whoosh_query(n, page_size)

    def _do_whoosh_query(self, n, page_size):
        """
        """
        from . import get_whoosh_index

        if self._searcher is None:
            ix = get_whoosh_index()
            self._searcher = ix.searcher()

        r = None
        results = self._searcher.search_page(self._query, n+1, pagelen=page_size)
        r = [x['data_obj'] for x in results]

        return r

