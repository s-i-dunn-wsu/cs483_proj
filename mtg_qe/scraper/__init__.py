# Samuel Dunn
# CS 483, Fall 2019

# This file makes the scraper module a python recognized module
# In addition, it supplies the function `cli_entry` for implementing
# the command line script `mtg_qe_scrape`

def cli_entry():
    import argparse
    import sys
    import shutil
    import os
    import tempfile
    import tarfile

    try:
        from .coordinator import Coordinator
        from .set_agent import SetAgent
    except ImportError:
        from mtg_qe.scraper.coordinator import Coordinator
        from mtg_qe.scraper.set_agent import SetAgent

    parser = argparse.ArgumentParser('mtg_qe_scrape')

    parser.add_argument('-i', '--intermediates-dir', type=str,
        help="Specifies a path to store intermediate files in. This will create the directory if necessary, as well as use the directory if present. Defaults to a system provided temporary directory")
    parser.add_argument('-o', '--output', type=str, help="The path to save the output archive to.")
    parser.add_argument('-n', '--num-agents', type=int, default=2, help="Specify the number of agents to utilize while scraping. (equates to number of threads used.)")
    args = parser.parse_args()

    # Set up the intermediates directory.
    if args.intermediates_dir:
        if not os.path.exists(args.intermediates_dir):
            os.makedirs(args.intermediates_dir)

        Coordinator.intermediates_dir = args.intermediates_dir
    else:
        Coordinator.intermediates_dir = tempfile.mkdtemp()

    # do the scraping bit.
    coord = Coordinator(args.num_agents)
    agents = [SetAgent(coord) for _ in range(args.num_agents)]

    for agent in agents:
        agent.start()

    try:
        for process in (agent._thread for agent in agents):
            while process.exitcode is None:
                process.join(0.25)

    except KeyboardInterrupt:
        coord._kill_flag.set()
        success = False
        for process in (agent._thread for agent in agents):
            process.join()
    else:
        success = True

    if success:
        # now within the intermediates folder there should be:
        #   an artwork dir
        #   a sets dir
        # We want both, so lets move them into a single folder and
        # tar that.
        os.mkdir(os.path.join(Coordinator.intermediates_dir, 'raw_data'))
        shutil.move(os.path.join(Coordinator.intermediates_dir, 'sets'), os.path.join(Coordinator.intermediates_dir, 'raw_data', 'sets'))
        shutil.move(os.path.join(Coordinator.intermediates_dir, 'artwork'), os.path.join(Coordinator.intermediates_dir, 'raw_data', 'artwork'))

        # now we're ready to tar it all.
        try:
            with open(tarfile.open(args.output, 'w:gz')) as tar:
                tar.add(os.path.join(Coordinator.intermediates_dir, 'raw_data'))
        except Exception:
            raise # not trying for the execption clause
        finally:
            if args.intermediates_dir is None:
                # we're using a temp dir.
                shutil.rmtree(Coordinator.intermediates_dir)
    else:
        # again, need to make sure we clean up after ourselves.
        if args.intermediates_dir is None:
            shutil.rmtree(Coordinator.intermediates_dir)