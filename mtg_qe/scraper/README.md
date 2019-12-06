This folder defines the scraper component of the project

Due to the sheer size of the dataset, we opted for an approach that could be stopped and resumed and ideally parallelized.

This module contains a solution fitting that criteria.

`Coordinator` is a class defined in `coordinator.py` that manages identifying discrete tasks, in this case MTG expansions, and providing those tasks to `Agent`s.

`Agent` Is an abstract representation of what a task-fulfilling agent should do.
`SetAgent` provides the implementation specific to scraing whole sets.

Files are stored in the coordinator's intermediates directory (specified by the user at scrape launch.)

If the job is paused, the Coordinator and Agetns can inspect the "intermediates" directory to resume where they were.
