# Samuel Dunn
# CS 483, Fall 2019

import os
import json
import logging
import tempfile

from ..utils.json_helpers import CardEncoder

class IndexInitializer(object):
    """
    This class oversees the creation of the internal index and whoosh index from
    the set data scraped by the `scraper` module.

    For reference, this is the second part of the full pipeline.
    Where [] and | denote a stage in the process, and () denotes outputs/inputs

    [scrape]+--> (artwork) -------------------------------------------> |              |
            +--> (sets) -----> [index_setup] +----> (whoosh_index) ---> | corpus setup | -> (corpus_data)
                                             +--> (internal_index) ---> |              |
    """
    def __init__(self, path_to_sets, temp_path):
        self._log = logging.getLogger("II")
        self._path = path_to_sets
        self._workspace = temp_path
        if not os.path.exists(path_to_sets):
            raise ValueError(f"Unable to initialize index with non existent directory: {path_to_sets}")

    def init_indexes(self):
        """
        Iterates over all set files found in the set directory supplied at construction
        and populates the whoosh index as well as the 'internal index'.

        Returns a handle to both as a tuple (whoosh_index, internal_index)
        """
        from ..model.card import Card
        from whoosh.index import create_in
        from .whoosh_integrations import make_whoosh_schema

        whoosh_index = create_in(os.path.join(self._workspace, 'whoosh_index'), make_whoosh_schema())
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
        with open(os.path.join(self._workspace, "internal_index.json"), 'w') as fd:
            json.dump(internal_index, fd, cls=CardEncoder)

        return whoosh_index, internal_index

def cli_entry():
    """
    This function is called as the entry point to the command line script:
    mtg_qe_init_index
    """
    import argparse
    import tarfile
    parser = argparse.ArgumentParser('mtg_qe_init_index')
    parser.add_argument('-f', '--folder', type=str, required=True, help="path to the set data generated by the scraper")
    parser.add_argument('-o', '--output', type=str, required=True, help="The path to save the output to. Output will be a .tar.gz archive, name accordingly")


    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as td:
        ii = IndexInitializer(args.folder, td)
        w_idx, i_idx = ii.init_indexes()

        # now have 2 things in td, a whoosh_index folder
        # and a internal_index.json file.

        # Package them up and save to output file.
        with tarfile.TarFile(args.output, "w:gz") as tar:
            tar.add(os.path.join(td, 'internal_index.json'), arc_name = "internal_index.json")
            tar.add(os.path.join(td, 'whoosh_index'), arc_name = 'whoosh_index')
