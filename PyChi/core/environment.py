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
#==========================================================
# IMPORTS
#==========================================================
from simpy import AnyOf
import simpy

# ==========================================================
# Environment
# ==========================================================
class Environment(simpy.Environment):

    # Alternative for now (similar to Chi)
    def time(self):
        return self.now()

    # Alternative for timeout (similar to Chi)
    def delay(self, t):
        return self.timeout(t)

    # ==========================================================
    # Execute statement
    # ==========================================================
    @staticmethod
    def execute(communicator):
        communicator.start_process()

        return communicator.process

    # ==========================================================
    # Select statement
    # ==========================================================
    def select(self, *communicators):
        # Removes all communicators of NoneType (for which the guard is false)
        communicators = [c for c in communicators if c]

        # Check if the correct input is given, and if not, give an error.
        for c in communicators:
            if not isinstance(c, Channel.Communicator):
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
            if c.process_started:
                raise ValueError(
                    'The communicator has already started its process,'
                    'which is not allowed when used with the select statement.'
                )

        # Only one communicator is selected. Every communicator must know who the other communicators are.
        # The reason is that the communicators must communicate to each other
        for c in communicators:
            other_communicators = [x for x in communicators if x != c]
            c.mutual_exclusive_communicators.extend(other_communicators)

        def select_process(env,communicators):
            # start the send/receive processes for all communicators.
            # The order in which processes are started determines their prioritization
            # In this case, the order is as given in the select function
            for c in communicators:
                c.start_process()

            # start waiting till one of the processes is selected
            events = [c.process for c in communicators if c]
            yield AnyOf(env, events)
            value = 0
            for c in communicators:
                if not c.process.triggered:
                    c.process.interrupt()
                if c.selected:
                    value = c.process.value
            return value

        return self.process(select_process(self, communicators))

    
# ==========================================================
# Selected function
# ==========================================================
def selected(communicator):
    if communicator is None:
        return False
    elif isinstance(communicator, Channel.Communicator):
        return communicator.selected
    else:
        raise TypeError(
            'The input is of the incorrect type.'
        )

# ==========================================================
# Process decorator
# ==========================================================
 def process(func):
    def wrapper(*args, **kwargs):
        """first argument of a process should be env"""
        if not isinstance(args[0], Environment):
            raise TypeError(
                'The first argument of a process should always'
                'be an Environment.'
            )
        env = args[0]
        return env.process(func(*args, **kwargs))
    return wrapper
