'''
This model showcases the complete simulation model of the end assignment
'''


from PyCh import *
import math
import time


# =================================
# Tote
# =================================
@dataclass
class Tote:
    entrytime: float = 0.0
    column: int = 0
    tier: int = 0


# =================================
# Global variables
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
# Generator
# =================================
@process
def Generator(env, sending_channel, Tier):
    ### BEGIN SOLUTION
    ta_dist = lambda: random.exponential(arrive)
    column_dist = lambda: random.randint(0, depth)
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
        yield env.execute(send)
        # delay = .....
        ### BEGIN SOLUTION
        delay = env.timeout(ta_dist())
        ### END SOLUTION
        yield delay


# =================================
# Demand Buffer
# =================================
@process
def Demand_Buffer(env, receiving_channel, sending_channel):
    xs = []  # list of totes
    while True:
        ### BEGIN SOLUTION
        sending = sending_channel.send(xs[0]) if len(xs) > 0 else None
        receiving = receiving_channel.receive()

        yield env.select(sending, receiving)
        if selected(sending):
            xs = xs[1:]
        if selected(receiving):
            x = receiving.entity
            xs = xs + [x]
        ### END SOLUTION


# =================================
# Vehicle
# =================================
@process
def Vehicle(env, receiving_channel, sending_channel):
    ### BEGIN SOLUTION
    while True:
        receive = receiving_channel.receive()
        x = yield env.execute(receive)

        distance = dv * (x.column+1)
        if distance <= vmaxv ** 2 / av:
            te_processing = 4 * math.sqrt( distance / av) + 2*lv
        else:
            te_processing = 2*(distance / vmaxv + vmaxv / av + lv)

        yield env.timeout(te_processing)

        send = sending_channel.send(x)
        yield env.execute(send)
        ### END SOLUTION


# =================================
# Buffer
# =================================
@process
def Buffer(env, receiving_channels, sending_channel, call_lift_channel):
    xs = []
    n = [0] * Level
    while True:
        sending = sending_channel.send(xs[0]) if len(xs) > 0 else None
        receiving = [receiving_channels[Tier].receive() if n[Tier] < bc else None for Tier in range(Level)]
        call_lift = call_lift_channel.send(xs[0].tier) if len(xs) > 0 else None
        communications = receiving + [call_lift] + [sending]
        yield env.select(*communications)

        for Tier in range(Level):
            if selected(receiving[Tier]):
                x = receiving[Tier].entity
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
# Lift
# =================================
@process
def Lift(env, receiving_channel, call_lift_channel, sending_channel):
    while True:
        ### BEGIN SOLUTION
        lift_called = call_lift_channel.receive()
        requested_tier = yield env.execute(lift_called)

        distance = dl * (requested_tier+1)
        if distance <= vmaxl ** 2 / al:
            t_travel = math.sqrt(4 * distance / al)
            t_e = (2*sqrt(distance / al) + ll)
        else:
            t_travel = 2 * vmaxl / al + (distance - vmaxl ** 2 / al) / vmaxl
            t_e = (distance / vmaxl + vmaxl / al + ll)

        yield env.timeout( t_e )
        # yield env.timeout(t_travel + ll)

        receive = receiving_channel.receive()
        x = yield env.execute(receive)

        yield env.timeout(t_e)

        send = sending_channel.send(x)
        yield env.execute(send)
        ### END SOLUTION


# =================================
# Exit
# =================================
@process
def Exit(env, receiving_channel):
    mphi = 0.0
    timer = time.time()
    for i in range(1, number_of_orders + 1):
        receive = receiving_channel.receive()
        x = yield env.execute(receive)

        mphi = (i - 1) / i * mphi + (env.now - x.entrytime) / i
        # print("tote = %d; Entrytime = %10.4f; Column = %2d; Mean throughput = %8.6f; Mean flowtime = %6.4f\n" %
        #      (i , x.entrytime, x.column, i / env.now, mphi ) )

        # Calculate speed of simulation
        if i % 10000 == 0:
            print("--- Totes %s - %s took %s seconds ---" % (i - 10000, i, time.time() - timer))
            timer = time.time()
    return mphi


# =================================
# GDV
# =================================
def GDV(env, sending_channel, Tier):
    a = Channel(env)  # for sending totes
    b = Channel(env)  # for sending totes
    G = Generator(env, a, Tier)
    D = Demand_Buffer(env, a, b)
    V = Vehicle(env, b, sending_channel)


# =================================
# Model
# =================================
def model():
    start_time = time.time()
    env = Environment()
    c = [Channel(env) for Tier in range(Level)]  # a channel for each tier, each sending totes
    d = Channel(env)  # for sending totes
    e = Channel(env)  # for calling the lift
    f = Channel(env)  # for sending totes

    GDVs = [GDV(env, c[Tier], Tier) for Tier in range(Level)]
    B = Buffer(env, c, d, e)
    L = Lift(env, d, e, f)
    E = Exit(env, f)
    env.run(until=E)
    print("simulation has ended")

    print("--- %s seconds ---" % (time.time() - start_time))
    print("--- mphi is %s ---" % E.value)

# =================================
# Main
# =================================
model()
