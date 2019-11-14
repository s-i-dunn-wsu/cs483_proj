# Samuel Dunn
# CS 483, Fall 2019
# This module implements the coordinator class,
# which is responsible for knowing, storing, and retrieving,
# the current progress of scraping, and delegating tasks out
# to any scrape agents.

# external imports
from bs4 import BeautifulSoup as bs
import multiprocessing as mp
import logging
import json
import re
import os

# project imports
try:
    from .request_regulator import RequestRegulator
    from ..model.card import Card
    from ..utils.json_helpers import CardEncoder
    from ..utils.path_helpers import  normalize_name

except ImportError:
    # hopefully we don't tear module... :shrug:
    from mtg_qe.scraper.request_regulator import RequestRegulator
    from mtg_qe.model.card import Card
    from mtg_qe.utils.json_helpers import CardEncoder
    from mtg_qe.utils.path_helpers import  normalize_name

class Coordinator(object):
    task_incomplete = object() # identity used to signal that an agent was unable to complete a task.
    intermediates_dir = None # this gets set to specify where to save intermediate content.

    def __init__(self, num_threads = 2):
        # Create the request regulators.
        # The initializing work will just use regulator 0.
        self._regulators = [RequestRegulator('https://gatherer.wizards.com') for _ in range(num_threads)]
        self._regulator_usage = {x : False for x in self._regulators}

        # Concurrency stuff:
        self._kill_flag = mp.Event()     # Used to signal threads to stop.
        self._regulator_lock = mp.Lock() # Used to be sure there aren't concurrent calls to regulator scheduling.

        # other stuff
        self._log = logging.getLogger("Coordinator")

        # First, need to build a list of all sets.
        # the method we've found to be consistent (even though its a smidge cheesy)
        # is to find the <select> field on gatherer's default search page and load a list
        # of all the sets from its options.

        soup = bs(self._regulators[0].get('/Pages/Default.aspx'), features='html.parser')

        # now find the tag we want:
        select_tag = soup.find('select', id='ctl00_ctl00_MainContent_Content_SearchControls_setAddText')

        # build a list of all set names:
        self._set_names = [x['value'] for x in select_tag.find_all('option')]

        # Now compare the list of set names to the 'completed' sets, stored (relative to execution)
        # at 'intermediate/sets/{set_name}_mtg_set.json'

        # ensure folders the scraper depends on existing are present.
        for subdir in ('sets', 'cards'):
            try:
                os.mkdir(os.path.join(Coordinator.intermediates_dir, subdir))
            except OSError:
                pass # already exists

        self._intermediates_path = os.path.join(Coordinator.intermediates_dir, 'sets')
        # Load the list of completed modules, create a to_do list which is the difference between the two.
        self._completed = [x.group(1).replace('_', ' ') for x in (re.match(r'(.*)_mtg_set.json', f) for f in os.listdir(self._intermediates_path)) if x]

        self._to_do = mp.Queue()
        for item in (x for x in self._set_names if x not in self._completed):
            if item:    # filter out empty strings.
                self._to_do.put(item)

    def get_next_task(self):
        """
        Called by any scraping agents to request the next task.

        .. warn::
            Will block until resources are made available by a corresponding call to `task_complete`

        :return: a tuple of relevant task data. (set name, regulator), where the regulator is the RequestRegulator tasked out to that job.
        :rtype: tuple
        """
        with self._regulator_lock:
            # Find a regulator not in use.
            if all([self._regulator_usage[x] for x in self._regulators]):
                self._log.warn("Out of free regulators! An agent must not have returned one to the Coordinator.")
                return None # kill the agent. RIP agent.

            if self._to_do.empty():
                return None

            # find a free regulator:
            regulator = [x for x in self._regulators if not self._regulator_usage[x]][0]
            set_task = self._to_do.get()

            return set_task, regulator


    def task_complete(self, set_name, regulator, data):
        # Called at the end of a worker threads task to signal the task is done
        # Dump ata to an intermediate file. data is presumably a dictionary or list of some kind
        # containing model.Card objects.
        # Since we don't (yet) know the exact layout, let's use a custom json encoder.
        if data is not Coordinator.task_incomplete:
            self._completed.append(set_name)

            with open(os.path.join(self._intermediates_path, normalize_name(set_name) + "_mtg_set.json"), 'w', encoding='utf-8') as fd:
                json.dump(data, fd, cls=CardEncoder)

        # Lastly, free the regulator.
        if regulator in self._regulators:
            with self._regulator_lock:
                self._regulator_usage[regulator] = False

    @property
    def is_open(self):
        return not self._kill_flag.is_set()

    def close(self):
        self._kill_flag.set()

        # close and join self._to_do as well if that's causing an issue.