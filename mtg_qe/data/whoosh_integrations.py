# Samuel Dunn
# CS 483, Fall 2019

import os
from whoosh import fields, index

def make_whoosh_schema():
    """
    Creates and returns the whoosh schema being used.
    """

    schema = fields.Schema(name = fields.TEXT,
                            rules_text = fields.TEXT,
                            flavor_text = fields.TEXT,
                            sets = fields.KEYWORD,
                            types = fields.KEYWORD,
                            subtypes = fields.KEYWORD,
                            data_obj = fields.STORED)
    return schema


def get_index_object():
    """
    creates the whoosh index in ./whoosh_index if it does not already exist.
    otherwise creates an index in ./whoosh_index.
    returns the index handle.
    """
    if not os.path.exists("whoosh_index"):
        os.mkdir("whoosh_index")
        return index.create_in(os.path.abspath("whoosh_index"), make_whoosh_schema())
    else:
        return index.open_dir(os.path.abspath('whoosh_index'))
