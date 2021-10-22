"""
The SimPy Environment is extended with the execute and select functions.
These are used to make simulation in SimPy more similar to Chi.

These execute function is used to execute a communicator.
E.g. Environment.execute( Channel.receive() )
Which executes a receive task.

The select function is used to execute ONLY one of the given communicators, 
When one is executed, the other communicators all are aborted.
E.g. Environment.select( Channel.receive(), Channel.send(entity) )
Which executes EITHER a receive or a send.

"""
# ==========================================================
# IMPORTS
# ==========================================================
import simpy
from simpy import AnyOf
from numpy import random
from PyCh import Communicator


# ==========================================================
# Environment
# ==========================================================
class Environment(simpy.Environment):

    @property
    def time(self):
        """ Returns the current simulation time

        This is an alternative to environment.now more similar to Chi

        :return: the current simulation time
        """
        return self.now

    def delay(self, time):
        """ Can be used to delay a process for a specific duration

        This is an alternative to environment.timeout() more similar to Chi
        can be used in a process using "yield environment.delay(time)"

        :param time: the (simulation) time duration during which the process must wait
        :return: a SimPy timeout event
        """
        return self.timeout(time)

    @staticmethod
    def execute(communicator):
        """ Used to communicate over a channel using "yield environment.execute(communicator)"

        This function can be used in a process to communicate over a channel.
        It is used as following: "yield environment.execute(communicator)"
        The process will continue after the yield statement when communication has occurred.

        When used with a receiver it can also be used as "entity = yield environment.execute(receiver)"
        to return the received entity. This can also be obtained later using receiver.entity

        :param communicator: The communicator (sender/receiver)
        """
        communicator.start_process()

        return communicator.communication

    def select(self, *communicators):  # TODO: documentation
        """ The select function allows a process to wait for one of a list senders/receivers to communicate.

        This is useful if it is unknown which communicator (sender/receiver) will first be ready.
        The process will wait till one of the communicators has communicated (which is the selected communicator),
        at which point communication by the other communicators is 'aborted'.
        If multiple communicators are able to communicate at the same time, then only one is selected at random.

        Can be used through either:

        - "environment.select(*communicators)"
        - or "environment.select(communicator1, communicator2, ...)"
        - or a combination of both: "environment.select(*communicators123, communicator4, ...)"

        The process will continue after the yield statement when communication has occurred.

        If at least one of the communicators is a receiver, then:
        "entity = yield environment.select(*communicators)"
        returns the received entity if a receiver is selected.
        If a sender is selected, the yield statement returns None

        :param communicators: the communicators of which only one will be selected
        """

        # Removes all communicators of NoneType (for which the guard is false)
        communicators = [c for c in communicators if c]
        # Check if the correct input is given, and if not, give an error.
        for c in communicators:
            if not isinstance(c, Communicator):
                if isinstance(c, simpy.Process):
                    raise TypeError(
                        'A process was passed to the Select statement, '
                        'Try a communicator instead.'
                    )
                else:
                    raise TypeError(
                        'One of the communicators is of an incorrect type.'
                    )
            if self != c.env:
                raise ValueError(
                    'It is not allowed to mix events from different '
                    'environments'
                )
            if c.communication_started:
                raise ValueError(
                    'The communicator has already started its process,'
                    'which is not allowed when used with the select statement.'
                )

        # Only one communicator is selected. Every communicator must know who the other communicators are.
        # The reason is that the communicators must communicate to each other
        for c in communicators:
            other_communicators = [x for x in communicators if x != c]
            c.mutual_exclusive_communicators.extend(other_communicators)

        def _select_process(env, communicators):
            """ the selection process used by the select statement"""

            # start the send/receive processes for all communicators.
            # The order in which processes are started determines their prioritization
            # We reshuffle this order randomly to randomize prioritization
            # Note: it would also be acceptable to keep the order of the list unchanged.
            random.shuffle(communicators)
            for c in communicators:
                c.start_process()

            # start waiting till one of the processes is selected
            events = [c.communication for c in communicators]
            yield AnyOf(env, events)

            entity = None
            for c in communicators:
                if c.selected:
                    entity = c.communication.value
            return entity

        return self.process(_select_process(self, communicators))


# ==========================================================
# Selected function
# ==========================================================
def selected(communicator):
    """ Used to evaluate if a communicator has been selected.

    :param communicator: the communicator (sender/receiver)
    :return: a bool which denotes if the communicator has been selected or not
    """
    if communicator is None:
        return False
    elif isinstance(communicator, Communicator):
        return communicator.selected
    else:
        raise TypeError(
            'The input is of the incorrect type.'
        )


# ==========================================================
# Process decorator
# ==========================================================
def process(func):
    """ A decorator for process definitions.

    The first argument of a process should always be its environment, e.g.:

    @process
    def Server(env,...):
        ...

    Look up python decorators for more information.
    """
    def wrapper(*args, **kwargs):
        """"""
        # first check if any of the arguments is an environment
        env = None
        for arg in args:
            if isinstance(arg, Environment):
                env = arg

        if not env:
            raise TypeError(
                'The first argument of a process should always'
                'be its Environment.'
            )
        return env.process(func(*args, **kwargs))

    return wrapper
