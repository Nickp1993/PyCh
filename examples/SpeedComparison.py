'''
This model is used to execute a speed comparison between PyCh and Chi3
'''

from PyCh import *
import time

# =================================
# Tote
# =================================
@dataclass
class Job:
    entrytime: float = 0
    time_entered_buffer: float = 0


# =================================
# Generator
# =================================
@process
def Generator(env, a, ta):
    while True:
        yield env.execute( a.send(env.now) )
        yield env.timeout(ta)


# =================================
# Buffer
# =================================
@process
def Buffer(env, a, b):
    xs = []  # list of jobs
    while True:
        receiving = a.receive()
        sending = b.send(xs[0]) if len(xs) > 0 else None
        yield env.select(sending, receiving)
        if selected(sending):
            xs = xs[1:]
        if selected(receiving):
            xs = xs + [receiving.entity]


# =================================
# Machine
# =================================
@process
def Server(env, a, b, ts):
    while True:
        x = yield env.execute( a.receive() )
        yield env.timeout(ts)
        yield env.select( b.send(x) )


# =================================
# Exit
# =================================
@process
def Exit(env, a, N):
    timer = time.time()
    for i in range(N):
        x = yield env.execute( a.receive() )
        if i % 20000 == 0:
            print("--- Totes %s - %s took %s seconds ---" % (i - 20000, i, time.time() - timer))
            timer = time.time()


# =================================
# Model
# =================================
def model():
    start_time = time.time()

    env = Environment()

    ta = 1.0
    ts = 1.0
    N = 1000000

    a = Channel(env)
    b = Channel(env)
    c = Channel(env)

    G = Generator(env, a, ta)
    B = Buffer(env, a, b)
    M = Server(env, b, c, ts)
    E = Exit(env, c, N)

    env.run(until=E)

    print("--- %s seconds ---" % (time.time() - start_time))


# =================================
# Main
# =================================
model()
