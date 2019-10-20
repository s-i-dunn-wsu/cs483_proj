# This is a quick and dirty script to test progress.

import sys
from mtg_qe.scraper.coordinator import *
from mtg_qe.scraper.set_agent import *

if __name__ == "__main__":
	c = Coordinator(4)
	agents = [SetAgent(c) for _ in range(4)]
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

