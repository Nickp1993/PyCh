"""
A Channel can be used by SimPy processes to send and receive entities over.

A Channel must first be defined using Channel(env) with env as the SimPy environment.
After that, process can use send(entity) or receive() to send and receive entities using this channel.
These entities can be any type of object.

A sender waits till a receiver is ready to receive.
A receiver waits till a sender is ready to receive.
If there are multiple receivers waiting, then a sender chooses one at random to send to.
If there are multiple senders waiting, then a receiver chooses one at random to receive from.

These channels are based on the channels used in Chi
See: https://cstweb.wtb.tue.nl/chi/trunk-r9682/tutorial/channels.html#a-channel

"""
# ==========================================================
# IMPORTS
# ==========================================================
from numpy import random


# ==========================================================
# Channel
# ==========================================================
class Channel:
    """ A channel through which communication can occur between senders and receivers."""

    def __init__(self, env):
        self.env = env  # The simulation environment in which this channel operates
        self.senders = []  # list of senders which are ready to send
        self.receivers = []  # list of receivers which are ready to receive

    def get_senders(self):
        """ Gets the list of all registered senders on this channel

        :return: the list of registered senders on this channel
        :rtype: list[Sender]
        """
        return self.senders

    def get_receivers(self):
        """ Gets the list of all registered receivers on this channel

        :return: the list of registered receivers on this channel
        :rtype: list[Receiver]
        """
        return self.receivers

    def get_random_receiver(self):
        """ Gets a random receiver from the list of registered receivers

        :return: a random receiver
        :rtype: Receiver
        """
        receiver = random.choice(self.get_receivers())
        return receiver

    def get_random_sender(self):
        """ Gets a random sender from the list of registered senders

        :return: a random sender
        :rtype: Sender
        """
        sender = random.choice(self.get_senders())
        return sender

    def get_env(self):
        """ Gets the simulation environment in which this channel operates

        :return: the simulation environment
        :rtype: Environment
        """
        return self.env

    def register_sender(self, sender):
        """ A function to register senders at this channel

        :param sender: the Sender
        """
        self.senders.append(sender)

    def unregister_sender(self, sender):
        """ A function to unregister senders from this channel

        :param sender: the Sender
        """
        if sender in self.get_senders():
            self.senders.remove(sender)

    def register_receiver(self, receiver):
        """ A function to register receivers at this channel

        :param receiver: the Receiver
        """
        self.receivers.append(receiver)

    def unregister_receiver(self, receiver):
        """ A function to unregister receivers from this channel

        :param receiver: the Receiver
        """
        if receiver in self.get_receivers():
            self.receivers.remove(receiver)

    def send(self, entity=None):
        """ A function which creates a Sender, ready to send an entity.

        Can be used in a process to send entities if followed by either:
        "yield environment.execute(Sender)"
        or
        "yield environment.select(Sender, *other_communicators)"
        See Environment.execute() or Environment.select() for more information.

        :param entity: the entity which is sent over this channel
        :return: Sender
        """
        return Sender(self.env, self, entity)

    def receive(self):
        """ A function which creates a Receiver, ready to receive an entity.

        Can be used in a process to send entities if followed by either:
        "yield environment.execute(Receiver)"
        or
        "yield environment.select(Receiver, *other_communicators)"
        See Environment.execute() or Environment.select() for more information.

        :return: Receiver
        """
        return Receiver(self.env, self)

    def try_communication(self):
        """ If both a sender and receiver are ready to communicate,
        communication occurs between a randomly chosen sender and receiver

        If both a sender and receiver are ready to communicate,
        a random sender and receiver are chosen.
        Both sender and receiver are then unregistered.
        If either sender or receiver were executed using select statement, then all other
        communicators in the select statement are also unregistered.
        Finally, communication occurs between the sender and receiver.

        """
        if self.get_senders() and self.get_receivers():
            sender = self.get_random_sender()
            receiver = self.get_random_receiver()

            # TODO: currently, entities cannot be sent and received by the same process. should this be allowed?
            if receiver in sender.mutual_exclusive_communicators or sender in receiver.mutual_exclusive_communicators:
                raise ValueError("a process cannot send to itself")

            sender.unregister_unselected_communicators()
            receiver.unregister_unselected_communicators()

            self.unregister_sender(sender)
            self.unregister_receiver(receiver)

            sender.communication.succeed()
            receiver.entity = sender.entity
            receiver.communication.succeed(value=receiver.entity)

    # ==========================================================
    # Communicator
    # ==========================================================


class Communicator:
    """ A communicator communications across a channel, it is either a Sender or Receiver.

    """

    def __init__(self, env, channel):
        """

        :param env: the environment in which this communicator operates
        :param channel: the channel over which this communicator communicates
        """
        self.env = env  # The environment of this communicator
        self.channel = channel  # The channel of this communicator
        self.communication = self.env.event()  # An event which is triggered when communication begins
        self.mutual_exclusive_communicators = []  # When this communicator is 'selected', these communicators are
        # unregistered from their channels
        self.communication_started = False  # is true if this communicator has started communicating

        self.register()  # registers the communicator to its channel

    def execute(self):
        """ Executes the communication of the communicator and returns its communication event

        Can be used as following: "yield communicator.execute()"
        Which is identical to "yield environment.execute(communicator)"

        :return: the communication event of this communicator
        """
        self.start_process()
        return self.communication

    # The function used to start the process
    def start_process(self):
        """ Starts the communication of the communicator, and asks its channel to check if communication is possible

        :return: the communication event of this communicator
        :rtype: Event
        """
        self.communication_started = True
        self.channel.try_communication()
        return self.communication

    @property
    def selected(self) -> bool:
        """ If a select statement is used, this property shows if this communicator was selected or not

        :return: a boolean which is true if the communicator was selected
        :rtype: bool
        """
        try:
            return self.communication.triggered
        except AttributeError:
            print("Oops! The process has not yet started.")

    def unregister_unselected_communicators(self):
        """ If this communicator was selected, this function is used to unregister the not selected communicators from
        their respective channels."""
        for c in self.mutual_exclusive_communicators:
            c.unregister()


# ==========================================================
# Sender
# ==========================================================
class Sender(Communicator):
    """ A sender is a type of communicator which sends"""
    def __init__(self, env, channel, entity=None):
        super().__init__(env, channel)
        self.entity = entity  # the entity which is sent

    def register(self):
        """ Register this sender at its channel"""
        self.channel.register_sender(self)

    def unregister(self):
        """ Unregister this sender at its channel"""
        self.channel.unregister_sender(self)


# ==========================================================
# Receiver
# ==========================================================
class Receiver(Communicator):
    """ A receiver is a type of communicator which receives"""
    def __init__(self, env, channel):
        super().__init__(env, channel)

    def register(self):
        """ Register this receiver at its channel"""
        self.channel.register_receiver(self)

    def unregister(self):
        """ Unregister this receiver from its channel"""
        self.channel.unregister_receiver(self)
