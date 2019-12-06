#!/usr/bin/env python3

# This script will run the projects scraper
# with out requiring the package to be installed.

import sys
import logging
import time
from mtg_qe.scraper import cli_entry

stime = time.strftime("%a%d%m%Y-%H%M")

# Log to a file
logging.basicConfig(level=logging.INFO, filename=f'scrape_{stime}.log')

# Uncomment to print logging info to stdout.
#logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

if __name__ == "__main__":
	cli_entry()