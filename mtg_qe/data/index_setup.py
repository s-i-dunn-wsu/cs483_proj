# Samuel Dunn
# CS 483, Fall 2019

import os
import json
import logging

from ..utils.json_helpers import CardEncoder

class IndexInitializer(object):
    """
    """
    def __init__(self, path_to_sets):
        self._log = logging.getLogger("II")
        self._path = path_to_sets
        if not os.path.exists(path_to_sets):
            raise ValueError(f"Unable to initialize index with non existent directory: {path_to_sets}")

    def init_indexes(self):
        """
        Iterates over all set files found in the set directory supplied at construction
        and populates the whoosh index as well as the 'internal index'.

        Returns a handle to both as a tuple (whoosh_index, internal_index)
        """
        from .whoosh_integrations import get_index_object
        from ..model.card import Card

        whoosh_index = get_index_object()
        whoosh_writer = whoosh_index.writer()
        internal_index = {'by_name': {}, 'by_multiverseid': {}}

        # used to know when we've passed a card quickly. (amortized O(1) if I remember correctly, once its big enough it'll be O(n))
        cards_by_name = set()

        # now for the meaty bit.
        # we're going to iterate over every set file, load its contents
        # then iterate over every card within, inflate it,
        # create a doc entry in the whoosh index for it, then store it within internal_index as well.
        # but only store in 'by_name' and the whoosh index if its the first unique occurrence of that card's name.
        for set_file in (os.path.join(self._path, x) for x in os.listdir(self._path) if x.endswith('mtg_set.json')):
            with open(set_file, encoding='utf-8') as fd:
                set_data = json.load(fd)

            self._log.info(f"Updating index with contents of {os.path.basename(set_file)}")
            for serialized_data in set_data:
                card = Card().deserialize(serialized_data)
                if card.name not in cards_by_name:
                    whoosh_writer.add_document(name=card.name,
                                               rules_text=card.text,
                                               flavor_text=card.flavor,
                                               sets=', '.join(card.other_prints),
                                               types=card.type,
                                               subtypes=card.subtypes,
                                               data_obj=card)
                    internal_index['by_name'][card.name] = card
                    cards_by_name.add(card.name)
                internal_index['by_multiverseid'][card.multiverseid] = card

        # write both indexes to disk.
        whoosh_writer.commit()
        with open("internal_index.json", 'w') as fd:
            json.dump(internal_index, fd, cls=CardEncoder)

        return whoosh_index, internal_index

def cli_entry():
    """
    This function is called as the entry point to the command line script:
    mtg_qe_init_index
    """
    import argparse
    parser = argparse.ArgumentParser('mtg_qe_init_index')
    parser.add_argument('-f', '--folder', type=str, required=True, help="path to the set data generated by the scraper")

    args = parser.parse_args()

    ii = IndexInitializer(args.folder)
    ii.init_indexes()