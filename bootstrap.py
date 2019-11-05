# This is a quick and dirty script to test progress.

import sys
import logging
import time
from mtg_qe.scraper.coordinator import *
from mtg_qe.scraper.set_agent import *

stime = time.strftime("%a%d%m%Y-%H%M")
logging.basicConfig(level=logging.INFO, filename=f'scrape_{stime}.log')

# Uncomment to print logging info to stdout.
# logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

if __name__ == "__main__":
	try:
		n = int(sys.argv[1])
	except Exception:
		n = 1
	finally:
		print(f"Running with {n} agents!")
	c = Coordinator(n)
	agents = [SetAgent(c) for _ in range(n)]
	for agent in agents:
		agent.start()

	try:
		for process in (agent._thread for agent in agents):
			while process.exitcode is None:
				process.join(0.25)

	except KeyboardInterrupt:
		c._kill_flag.set()
		for process in (agent._thread for agent in agents):
			process.join()
	sys.exit(0)

