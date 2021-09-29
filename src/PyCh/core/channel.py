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
#==========================================================
# IMPORTS
#==========================================================
import random as rand
import simpy


# ==========================================================
# Channel
# ==========================================================
class Channel:
    def __init__(self, env):
        self.env = env
        self.senders = []  # list of senders which are ready to send
        self.receivers = []  # list of receivers which are ready to receive

    def get_senders(self):
        return self.senders

    def get_receivers(self):
        return self.receivers

    @property
    def is_any_receiver_ready2receive(self) -> bool:
        receivers = self.get_receivers()
        ready2receive = True in (not r.communicate.triggered and not r.abort for r in receivers)
        return ready2receive

    def get_receivers_ready2receive(self):
        receivers = self.get_receivers()
        receivers_ready2receive = [r for r in receivers if r.ready]
        return receivers_ready2receive

    def get_random_receiver_ready2receive(self):
        receivers_ready2receive = self.get_receivers_ready2receive()
        receiver = rand.choice(receivers_ready2receive)
        return receiver

    @property
    def is_any_sender_ready2send(self) -> bool:
        senders = self.get_senders()
        ready2send = True in (not s.communicate.triggered and not s.abort for s in senders)
        return ready2send

    def get_senders_ready2send(self):
        senders = self.get_senders()
        senders_ready2send = [s for s in senders if s.ready]
        return senders_ready2send

    def get_random_sender_ready2send(self):
        senders_ready2send = self.get_senders_ready2send()
        sender = rand.choice(senders_ready2send)
        return sender

    def get_env(self):
        return self.env

    def register_sender(self, sender):
        self.senders.append(sender)

    def remove_sender(self, sender):
        self.senders.remove(sender)

    def register_receiver(self, receiver):
        self.receivers.append(receiver)

    def remove_receiver(self, receiver):
        self.receivers.remove(receiver)

    def send(self, entity=None):
        return self.Sender(self.env, self, entity)

    def receive(self):
        return self.Receiver(self.env, self)    
        
    # ==========================================================
    # Communicator
    # ==========================================================
    class Communicator:
        def __init__(self, env, channel):
            self.env = env  # The environment of this communicator
            self.channel = channel  # The channel of this communicator
            self.abort = False  # When a select statement is used, abort turns true if this communicator is not selected
            self.communicate = self.env.event()  # An event which is triggered when communication begins
            self.mutual_exclusive_communicators = []  # When a select statement is used, this are the other communicators up for selection
            self.process = []  # The process of this communicator
            self.process_started = False  # The process is initially not started

        '''
        We have removed this for now, as it might be confusing to students 
        '''
        # Calling This communicator (e.g. Communicator()() )
        # starts the process (if not already started) and returns it
        # def __call__(self):
        #     if not self.process_started:
        #         self.start_process()
        #     return self.process

        # executes the process (if not already started) and returns it
        # Can be used as following: yield sender.execute()
        def execute(self):
            if not self.process_started:
                self.start_process()
            return self.process

        # If a select statement is used, this property shows if this communicator was selected
        @property
        def selected(self) -> bool:
            try:
                return self.process.triggered and not self.abort
            except AttributeError:
                print("Oops! The process has not yet started.")

        @property
        def ready(self) -> bool:
            return (not self.communicate.triggered) and (not self.abort)

        # The function used to start the process
        def start_process(self):
            self.process = self.env.process(self.communicationprocess())
            self.process_started = True

        # This function is called when this communicator is selected.
        # It aborts the communication of all other communicators.
        def cancel_mutual_exclusive_communicators(self):
            for c in self.mutual_exclusive_communicators:
                c.abort = True
                if isinstance(c, self.channel.Sender) and not c.communicate.triggered:
                    c.communicate.defused = True
                    c.communicate.fail(Exception('abort communicate'))
                elif isinstance(c, self.channel.Receiver) and not c.communicate.triggered:
                    c.communicate.defused = True
                    c.communicate.fail(Exception('abort communicate'))

    # ==========================================================
    # Sender
    # ==========================================================
    class Sender(Communicator):
        def __init__(self, env, channel, entity=None):
            super().__init__(env, channel)
            self.entity = entity

        def communicationprocess(self, entity=None):
            entity = self.entity
            receivers = self.channel.get_receivers()
            # if 1 or more receivers are waiting and not yet triggered
            # choose a receiver at random, trigger its ready event, and send it the entity
            if self.channel.is_any_receiver_ready2receive:
                if not self.abort:  # NEW
                    receiver = self.channel.get_random_receiver_ready2receive()
                    receiver.communicate.succeed(value=entity)
                    # abort communicate/communicate for all communicators which are mutually exclusive with this communicator
                    self.cancel_mutual_exclusive_communicators()
            # else, if no receiver is ready to receive, schedule an event that this sender is ready to send
            else:
                self.communicate = self.env.event()
                self.channel.register_sender(self)
                # wait till a receiver triggers the ready event of this sender
                # Then, trigger the ready event of the receiver, and send it the entity
                try:
                    receiver = yield self.communicate
                    if not self.abort:
                        receiver.communicate.succeed(value=entity)
                        # abort communicate/communicate for all communicators which are mutually exclusive with this communicator
                        self.cancel_mutual_exclusive_communicators()
                except simpy.Interrupt:
                    pass
                except Exception as e:
                    pass
                self.channel.remove_sender(self)
            return None

    # ==========================================================
    # Receiver
    # ==========================================================
    class Receiver(Communicator):
        def __init__(self, env, channel):
            super().__init__(env, channel)

        def communicationprocess(self):
            senders = self.channel.get_senders()
            # if 1 or more senders are waiting and not yet triggered, choose a sender at random
            # notify to the sender that this receiver is ready, and start waiting to receive the entity.
            if self.channel.is_any_sender_ready2send:
                if not self.abort:  # NEW
                    sender = self.channel.get_random_sender_ready2send()
                    self.communicate = self.env.event()
                    sender.communicate.succeed(value=self)
                    # abort communicate/communicate for all communicators which are mutually exclusive with this communicator
                    self.cancel_mutual_exclusive_communicators()
                    try:
                        self.received_entity = yield self.communicate

                        return self.received_entity
                    except Exception as e:
                        pass
            # else, if no sender is ready to send, schedule an event that this receiver is ready to receive
            else:
                self.communicate = self.env.event()
                self.channel.register_receiver(self)
                # wait till the sender sends the entity
                try:
                    self.received_entity = yield self.communicate
                    self.channel.remove_receiver(self)
                    if not self.abort:
                        # abort communicate/communicate for all communicators which are mutually exclusive with this communicator
                        self.cancel_mutual_exclusive_communicators()
                        return self.received_entity
                    else:
                        return None
                except simpy.Interrupt:
                    self.channel.remove_receiver(self)
                    return None
                except Exception as e:
                    self.channel.remove_receiver(self)
                    return None



