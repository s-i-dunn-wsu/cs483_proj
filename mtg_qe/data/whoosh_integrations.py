# Samuel Dunn
# CS 483, Fall 2019

import os
import whoosh

def make_whoosh_schema():
    """
    Creates and returns the whoosh schema being used.
    Note: typically you will want to retrieve the schema from
          the index itself (ix.schema).
          This function exists to create a schema object during
          the creation of the index.
    """
    from whoosh import fields
    schema = fields.Schema(name = fields.TEXT,
                            rules_text = fields.TEXT,
                            flavor_text = fields.TEXT,
                            sets = fields.KEYWORD(stored=True),
                            types = fields.KEYWORD(stored=True),
                            subtypes = fields.KEYWORD(stored=True),
                            power = fields.NUMERIC,
                            toughness = fields.NUMERIC,
                            cmc = fields.NUMERIC,
                            mana_cost = fields.KEYWORD,
                            white = fields.NUMERIC,
                            blue = fields.NUMERIC,
                            black = fields.NUMERIC,
                            red = fields.NUMERIC,
                            green = fields.NUMERIC,
                            legal_formats = fields.KEYWORD(stored=True),
                            data_obj = fields.STORED)
    return schema


def get_whoosh_index():
    """
    Locates, loads, and returns the whoosh index bundled with the package installation.
    """
    from . import get_data_location
    whoosh_path = os.path.join(get_data_location(), 'whoosh_index')
    return whoosh.index.open_dir(whoosh_path)
