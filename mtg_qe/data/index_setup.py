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

    This class manages the 'index_setup' stage, below there is a method `cli_entry`
    that manages this as the corpus setup stage.
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

        if not os.path.exists(os.path.join(self._workspace, 'whoosh_index')):
            os.mkdir(os.path.join(self._workspace, 'whoosh_index'))

        whoosh_index = create_in(os.path.join(self._workspace, 'whoosh_index'), make_whoosh_schema())
        whoosh_writer = whoosh_index.writer()
        internal_index = {'by_name': {}, 'by_multiverseid': {}}

        def fix_int_vals(n):
            try:
                None if n is None else int(n)
            except Exception:
                # this is a wild-card value (* is somewhere in there, there are also cards with text like '1+*')
                return None

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
                                               power = fix_int_vals(card.power),
                                               toughness = fix_int_vals(card.toughness),
                                               legal_formats = ', '.join(card.legal_formats),
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
    This cli entry point manages the entire life cycle after scraping
    and outputs a final corpus_files.tar.gz
    """
    import argparse
    import logging
    import os
    import tarfile
    import shutil
    import sys

    logger = logging.getLogger("init_corpus")
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser("mtg_qe_init_corpus")
    parser.add_argument('-i', '--input-targz', type=str, required=True, help="the path to the .tar.gz file scraping outputs.")
    parser.add_argument('-o', '--output', type=str, default='corpus_files.tar.gz', help="the name of the file to save corpus data to")

    args = parser.parse_args()

    if not tarfile.is_tarfile(args.input_targz):
        print(f"Cannot open tarfile given. {args.input_targz}", file=sys.stderr)
        sys.exit(1)

    # need a temp dir to extract scrape output to
    with tempfile.TemporaryDirectory() as scrape_dir:
        # extract tarfile stuff there.
        with tarfile.open(args.input_targz, mode='r:gz') as intar:
            logger.info("Extracting relevant scrape data...")
            intar.extractall(scrape_dir)

        # need a temp dir for write intermediate index data to.
        with tempfile.TemporaryDirectory() as td:
            # Prep the indexes
            logger.info("Building indexes")
            ii = IndexInitializer(os.path.join(scrape_dir, 'raw_data', 'sets'), td)
            ii.init_indexes()

            # now have 2 things in td, a whoosh_index folder
            # and a internal_index.json file.

            # Package them up and save to output file, along with the scrape's artwork dir.
            with tarfile.open(args.output, "w:gz") as tar:
                logger.info(f"Writing output to {args.output}...")
                tar.add(os.path.join(td, 'internal_index.json'), arcname = "corpus_files/internal_index.json")
                tar.add(os.path.join(td, 'whoosh_index'), arcname = 'corpus_files/whoosh_index')

                # Write the artwork contents in too
                tar.add(os.path.join(scrape_dir, 'raw_data', 'artwork'), arcname = 'corpus_files/artwork')

        logger.info("Cleaning up...")
    logger.info("Done! index build successful.")