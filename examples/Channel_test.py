'''
This script is to test if PyCh is able to handle many different sending and receiving events at the same time.
'''


from PyCh import *

# =================================
# Machines
# =================================
@process
def M1(env, sending_channels, receiving_channels ):
    for j in range(1,100):
        receiving = [r_c.receive() for r_c in receiving_channels]
        sending = [s_c.send(5) for s_c in sending_channels]
        yield env.select(*receiving,*sending)


@process
def M2(env, sending_channels, receiving_channels ):
    for j in range(1,100):
        sending = [s_c.send(5) for s_c in sending_channels]
        receiving = [r_c.receive() for r_c in receiving_channels]
        yield env.select(*sending,*receiving)


@process
def M3(env, s_c ):
    for j in range(1,100):
        send1 = s_c.send(10)
        send2 = s_c.send(11)
        yield env.select(send1,send2)


@process
def M4(env, r_c ):
    for j in range(1,100):
        receive1 = r_c.send(10)
        receive2 = r_c.send(11)
        yield env.select(receive1,receive2)


# =================================
# Model
# =================================
def model():
    env = Environment()
    Cs = [Channel(env) for z in range(1,5)]  # a channel for each tier, each sending totes

    M1s = [M1(env, Cs, Cs) for z in range(1,5)]
    M2s = [M2(env, Cs, Cs) for z in range(1,5)]
    M3s = [M3(env, c) for c in Cs]
    M4s = [M4(env, c) for c in Cs]

    env.run()
    print("simulation has ended")


# =================================
# Main
# =================================
model()
