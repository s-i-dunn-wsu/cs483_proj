# Samuel Dunn
# CS 483, Fall 2019

import multiprocessing as mp
import logging

try:
    from .coordinator import Coordinator
except ImportError:
    from mtg_qe.scraper.coordinator import Coordinator

class Agent(object):
    """
    An agent works with the Coordinator to fulfill tasks.
    """

    # Some custom exception classes.
    class IShouldDie(Exception): pass


    def __init__(self, coordinator):
        self._coordinator = coordinator
        self._thread = mp.Process(target=self._thread_function)

    def start(self):
        """
        Launches the agents thread.
        """
        self._thread.start()

    def join(self, timeout = None):
        """
        Blocks until the agent's thread terminates.
        """
        self._thread.join(timeout)

    def fetch_task(self):
        """
        Fetches the next task from coordinator.
        """
        self.__task = self._coordinator.get_next_task()
        if self.__task is None:
            # No tasks left in coordinator.
            raise Agent.IShouldDie

        self._prep_for_task(*self.__task)

    def task_complete(self, output):
        """
        Signals the coordinator that the task is done.
        """
        args = list(self.__task) + [output]
        self._coordinator.task_complete(*args)

    def task_incomplete(self):
        """
        Signals the coordinator that this task was not completed, for some reason.
        """
        args = list(self.__task) + [Coordinator.task_incomplete]


    def _thread_function(self):
        """
        This function is the main function of the Agent's thread.
        It runs through the cycle of fetching and completing tasks
        while the Coordinator is still open. (No kill signal set.)
        """
        # Get the next task.
        while self._coordinator.is_open:
            try:
                self.fetch_task()
            except Agent.IShouldDie:
                # No more tasks.
                logging.getLogger('Agent').debug("no more tasks for agent")
                return

            # Start building output for the task.
            output = []
            try:
                for item in self._generate_items():
                    output.append(item)
                    if not self._coordinator.is_open:
                        logging.getLogger('Agent').debug('coordinator closed, terminating early.')
                        return # Exit early, some one is probably waiting to join on this thread.

            except Exception as e:
                logging.getLogger("Agent").error("Caught an error in subclass hook.")
                logging.getLogger("Agent").error(e, exc_info=True)
                output = Coordinator.task_incomplete

            finally:
                self.task_complete(output)

    def _prep_for_task(self, *args):
        """
        This is a hook for subclasses.
        This is called when a task is loaded from the Coordinator.
        Subclasses are expected to use the given arguments to set up for the
        next task, cleaning any left overs from previous tasks, and acquiring
        assets necessary for the current one.
        """
        raise NotImplementedError

    def _generate_items(self):
        """
        This is a hook for subclasses.

        This method is used as a generator to iterate over elements
        It is expected that we get one piece of the task at a time, rather than
        all at once. This helps keep response time to user events (such as a keybaord
        interrupt) nice and quick.
        """
        raise NotImplementedError