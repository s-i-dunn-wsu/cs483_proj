# Samuel Dunn
# CS 483, Fall 2019

import os
import json
import logging
import tempfile

from ..utils.json_helpers import CardEncoder
from ..utils.mana import fix_variable_mana

class IndexInitializer(object):
    '''
    This class oversees the creation of the internal index and whoosh index from
    the set data scraped by the `scraper` module.

    For reference, this is the second part of the full pipeline.
    Where [] and | denote a stage in the process, and () denotes outputs/inputs

    [scrape]+--> (artwork) -------------------------------------------> |              |
            +--> (sets) -----> [index_setup] +----> (whoosh_index) ---> | corpus setup | -> (corpus_data)
                                             +--> (internal_index) ---> |              |

    This class manages the 'index_setup' stage, below there is a method `cli_entry`
    that manages this as the corpus setup stage.
    '''
    def __init__(self, path_to_sets, temp_path):
        self._log = logging.getLogger('II')
        self._path = path_to_sets
        self._workspace = temp_path
        if not os.path.exists(path_to_sets):
            raise ValueError(f'Unable to initialize index with non existent directory: {path_to_sets}')

    def init_indexes(self):
        '''
        Iterates over all set files found in the set directory supplied at construction
        and populates the whoosh index as well as the 'internal index'.

        Returns a handle to both as a tuple (whoosh_index, internal_index)
        '''
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
                return None if n is None else int(n)
            except Exception:
                # this is a wild-card value (* is somewhere in there, there are also cards with text like '1+*')
                return None

        def count_mana_symbols(card):
            if not card.mana_cost:
                return 0, 0, 0, 0, 0

            as_str = ''.join(card.mana_cost)
            return as_str.count('W'), as_str.count('U'), as_str.count('B'), as_str.count('R'),as_str.count('G')

        # used to know when we've passed a card quickly. (amortized O(1) if I remember correctly, once its big enough it'll be O(n))
        cards_by_name = set()

        # While we're cruising through everything we may as well also grab some useful data
        metadata = { 'expansions': set(),
                    'types' : set(),
                    'subtypes': set(),
                    'formats': set() }

        # now for the meaty bit.
        # we're going to iterate over every set file, load its contents
        # then iterate over every card within, inflate it,
        # create a doc entry in the whoosh index for it, then store it within internal_index as well.
        # but only store in 'by_name' and the whoosh index if its the first unique occurrence of that card's name.
        for set_file in (os.path.join(self._path, x) for x in os.listdir(self._path) if x.endswith('mtg_set.json')):
            with open(set_file, encoding='utf-8') as fd:
                set_data = json.load(fd)

            self._log.info(f'Updating index with contents of {os.path.basename(set_file)}')
            for serialized_data in set_data:
                card = Card().deserialize(serialized_data)
                # We're up against the wall, and need to fix the current scrape set with out a rescrape.
                # this function fixes the current-known mana issue.
                fix_variable_mana(card)

                if card.name not in cards_by_name:
                    # precompute some things, this makes the whoosh_writer.add_doc call somewhat cleaner
                    p, t = fix_int_vals(card.power), fix_int_vals(card.toughness)
                    cmc = fix_int_vals(card.cmc)
                    w, u, b, r, g = count_mana_symbols(card)
                    types = card.type.lower() if card.type else None
                    subtypes = card.subtypes.lower() if card.subtypes else None
                    rules_text = card.text.lower() if card.text else None
                    flavor = card.flavor.lower() if card.flavor else None

                    # shove everything into whoosh
                    whoosh_writer.add_document(name=card.name.lower(),
                                               rules_text=rules_text,
                                               flavor_text=flavor,
                                               sets=', '.join(card.other_prints).lower(),
                                               types=types,
                                               subtypes=subtypes,
                                               power = p, toughness = t,
                                               cmc = 0 if not cmc else cmc,
                                               mana_cost = ', '.join(card.mana_cost) if card.mana_cost else None,
                                               white = w, blue = u, black = b, red = r, green = g,
                                               legal_formats = ', '.join(card.legal_formats).lower(),
                                               data_obj=card)

                    # add to internal index and update card_by_name
                    internal_index['by_name'][card.name] = card
                    cards_by_name.add(card.name)

                    # While we're here we can update this info too:
                    # doing metadata updates here, rather than every card, should be fine
                    # since data that varies between multiple printings of each card
                    # should be reflected in the fields grabbed (expansions, old versions of new cards are standard legal, etc.)
                    metadata['expansions'].update(card.other_prints.keys())
                    if card.type:
                        metadata['types'].update([x.strip() for x in card.type.split()])
                    if card.subtypes:
                        metadata['subtypes'].update([x.strip() for x in card.subtypes.split()])
                    metadata['formats'].update(card.legal_formats)

                # Add all cards, regardless of name, to the 'by_multiverseid' section.
                internal_index['by_multiverseid'][card.multiverseid] = card

        # write both indexes to disk.
        whoosh_writer.commit()
        with open(os.path.join(self._workspace, 'internal_index.json'), 'w') as fd:
            # Before we dump stuff, lets go ahead and store the metadata info here too.
            # that way we don't have to write a nearly identical module for the metadata info as
            # we already have for internal_index.
            internal_index.update({k: sorted(v) for k, v in metadata.items()})
            json.dump(internal_index, fd, cls=CardEncoder)

        return whoosh_index, internal_index


def cli_entry():
    '''
    This cli entry point manages the entire life cycle after scraping
    and outputs a final corpus_files.tar.gz
    '''
    import argparse
    import logging
    import os
    import tarfile
    import shutil
    import sys

    logger = logging.getLogger('init_corpus')
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser('mtg_qe_init_corpus')
    parser.add_argument('-i', '--input-targz', type=str, required=True, help='the path to the .tar.gz file scraping outputs.')
    parser.add_argument('-o', '--output', type=str, default='corpus_files.tar.gz', help='the name of the file to save corpus data to')

    args = parser.parse_args()

    if not tarfile.is_tarfile(args.input_targz):
        print(f'Cannot open tarfile given. {args.input_targz}', file=sys.stderr)
        sys.exit(1)

    # need a temp dir to extract scrape output to
    with tempfile.TemporaryDirectory() as scrape_dir:
        # extract tarfile stuff there.
        with tarfile.open(args.input_targz, mode='r:gz') as intar:
            logger.info('Extracting relevant scrape data...')
            intar.extractall(scrape_dir)

        # need a temp dir for write intermediate index data to.
        with tempfile.TemporaryDirectory() as td:
            # Prep the indexes
            logger.info('Building indexes')
            ii = IndexInitializer(os.path.join(scrape_dir, 'raw_data', 'sets'), td)
            ii.init_indexes()

            # now have 3 things in td, a whoosh_index folder
            # and a internal_index.json file.

            # Package them up and save to output file, along with the scrape's artwork dir.
            with tarfile.open(args.output, 'w:gz') as tar:
                logger.info(f'Writing output to {args.output}...')
                tar.add(os.path.join(td, 'internal_index.json'), arcname = 'corpus_files/internal_index.json')
                tar.add(os.path.join(td, 'whoosh_index'), arcname = 'corpus_files/whoosh_index')

                # Write the artwork contents in too
                tar.add(os.path.join(scrape_dir, 'raw_data', 'artwork'), arcname = 'corpus_files/artwork')

        logger.info('Cleaning up...')
    logger.info('Done! index build successful.')