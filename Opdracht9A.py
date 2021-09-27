from numpy import random
from Course_4DC10.simChi.core.channel_select import Channel, process, selected, Environment
from dataclasses import dataclass
import simpy
import math
import numpy
numpy.seterr(divide='ignore')
import time


# =================================
# =================================
# =================================

start_time = time.time()


# =================================
# # Tote definition
# =================================
@dataclass
class Tote:
    entrytime: float = 0.0
    column: int = 0
    tier: int = 0


# =================================
# # Global variables
# =================================
lv = 3.0  # time to load/unload the vehicle
dv = 0.5  # unit width clearance
vmaxv = 1.5  # maximum velocity of the vehicle
av = 1.0  # acceleration/deceleration of the vehicle
ll = 2.0  # time to load/unload the lift
dl = 0.8  # unit height clearance
vmaxl = 5.0  # maximum velocity of lift
al = 7.0  # acceleration/deceleration of lift
bc = 1  # buffer capacity
arrive = 70.0  # inter arrival time of requests
Level = 9  # the number of tiers
depth = 55  # the number of columns
number_of_orders = 100000  # the number of orders to process


# =================================
# # Generator definition
# =================================
def Generator(env, sending_channel, Tier):
    ### BEGIN SOLUTION
    ta_dist = lambda: random.exponential(arrive)
    column_dist = lambda: random.randint(1, depth)
    ### END SOLUTION
    while True:
        x = Tote()
        x.entrytime = env.now
        # x.column = .....
        # x.tier = .....
        ### BEGIN SOLUTION
        x.column = column_dist()
        x.tier = Tier
        ### END SOLUTION
        send = sending_channel.send(x)
        yield env.select(send)
        # delay = .....
        ### BEGIN SOLUTION
        delay = env.timeout(ta_dist())
        ### END SOLUTION
        yield delay


# =================================
# # Demand Buffer definition
# =================================
def Demand_Buffer(env, receiving_channel, sending_channel):
    xs = []  # list of totes
    while True:
        ### BEGIN SOLUTION
        receiving = receiving_channel.receive()
        sending = sending_channel.send(xs[0]) if len(xs) > 0 else None
        yield env.select(sending, receiving)
        if selected(sending):
            xs = xs[1:]
        if selected(receiving):
            x = receiving.received_entity
            xs = xs + [x]
        ### END SOLUTION


# =================================
# # Vehicle definition
# =================================
def Vehicle(env, receiving_channel, sending_channel):
    ### BEGIN SOLUTION
    while True:
        receive = receiving_channel.receive()
        x = yield env.select(receive)

        distance = dv * x.column
        if distance <= vmaxv ** 2 / av:
            t_travel = math.sqrt(4 * distance / av)
        else:
            t_travel = 2 * vmaxv / av + (distance - vmaxv ** 2 / av) / vmaxv

        # TODO: eigenlijk zou je hier pas het item kunnen ophalen, maar zo wordt het niet gemodelleerd.
        # De reden is natuurlijk dat je in dat geval geen idee hebt waar je naartoe moet rijden. Dit zou eigenlijk eerst verstuurd moeten worden.
        #  x = yield receiving_channel.receive()
        # TODO: Daarnaast, zou je pas kunnen unloaden als er een plekje vrij is in de buffer.
        # Dus pas als de buffer ready is om te ontvangen, heb je nog lv seconden nodig om het ook echt in de buffer te plaatsen.
        #  yield env.timeout(t_travel)
        #  yield sending_channel.readyto_send()
        #  yield env.timeout(lv)
        #  yield sending_channel.send(x)
        te_processing = 2 * t_travel + 2 * lv
        yield env.timeout(te_processing)

        send = sending_channel.send(x)
        yield env.select(send)
        ### END SOLUTION


# =================================
# # Buffer definition
# =================================
def Buffer(env, receiving_channels, sending_channel, call_lift_channel):
    xs = []
    n = [0] * Level
    while True:
        receiving = [receiving_channels[Tier].receive() if n[Tier] < bc else None for Tier in range(Level)]
        call_lift = call_lift_channel.send(xs[0].tier) if len(xs) > 0 else None
        sending = sending_channel.send(xs[0]) if len(xs) > 0 else None
        communications = receiving + [call_lift] + [sending]
        yield env.select(*communications)

        for Tier in range(Level):
            if selected(receiving[Tier]):
                x = receiving[Tier].received_entity
                xs = xs + [x]
                n[Tier] = n[Tier] + 1

        if selected(call_lift):
            pass

        if selected(sending):
            ### BEGIN SOLUTION
            Tier = xs[0].tier
            xs = xs[1:]
            n[Tier] = n[Tier] - 1
            ### END SOLUTION


# =================================
# # Lift definition
# =================================
def Lift(env, receiving_channel, call_lift_channel, sending_channel):
    while True:
        ### BEGIN SOLUTION
        lift_called = call_lift_channel.receive()
        yield env.select(lift_called)
        requested_tier = lift_called.received_entity

        distance = dl * requested_tier
        if distance <= vmaxl ** 2 / al:
            t_travel = math.sqrt(4 * distance / al)
        else:
            t_travel = 2 * vmaxl / al + (distance - vmaxl ** 2 / al) / vmaxl
        yield env.timeout(t_travel + ll)

        receive = receiving_channel.receive()
        yield env.select(receive)
        x = receive.received_entity

        yield env.timeout(t_travel + ll)

        send = sending_channel.send(x)
        yield env.select(send)
        ### END SOLUTION


# =================================
# # Exit definition
# =================================
def Exit(env, receiving_channel):
    mphi = 0.0
    timer = time.time()
    for i in range(1, number_of_orders + 1):
        receive = receiving_channel.receive()
        yield env.select(receive)
        x = receive.received_entity

        mphi = (i - 1) / i * mphi + (env.now - x.entrytime) / i
        #         print("tote = %d; Entrytime = %10.4f; Column = %2d; Mean throughput = %8.6f; Mean flowtime = %6.4f\n" %
        #              (i , x.entrytime, x.column, i / env.now, mphi ) )

        # Calculate speed of simulation
        if i % 10000 == 0:
            print("--- Totes %s - %s took %s seconds ---" % (i - 10000, i, time.time() - timer))
            timer = time.time()


# =================================
## GDV definition
# =================================
def GDV(env, sending_channel, Tier):
    a = Channel(env)  # for sending totes
    b = Channel(env)  # for sending totes
    G = env.process(Generator(env, a, Tier))
    D = env.process(Demand_Buffer(env, a, b))
    V = env.process(Vehicle(env, b, sending_channel))

# =================================
# # Main
# =================================
env = Environment()
c = [Channel(env) for Tier in range(Level)]  # a channel for each tier, each sending totes
d = Channel(env)  # for sending totes
e = Channel(env)  # for calling the lift
f = Channel(env)  # for sending totes

GDVs = [GDV(env, c[Tier], Tier) for Tier in range(Level)]
B = env.process(Buffer(env, c, d, e))
L = env.process(Lift(env, d, e, f))
E = env.process(Exit(env, f))
env.run(until=E)
print("simulation has ended")

print("--- %s seconds ---" % (time.time() - start_time))