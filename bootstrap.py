# This is a quick and dirty script to launch the scraper
# in a dev environment

import sys
import logging
import time
from mtg_qe.scraper import cli_entry

stime = time.strftime("%a%d%m%Y-%H%M")
logging.basicConfig(level=logging.INFO, filename=f'scrape_{stime}.log')

# Uncomment to print logging info to stdout.
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

if __name__ == "__main__":
	cli_entry()