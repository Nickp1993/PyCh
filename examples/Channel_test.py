from PyCh import *
import math

# =================================
# # Machine definition
# =================================
def M1(env, sending_channels, receiving_channels ):
    for j in range(1,100):
        receiving = [r_c.receive() for r_c in receiving_channels]
        sending = [s_c.send(5) for s_c in sending_channels]
        yield env.select(*receiving,*sending)

def M2(env, sending_channels, receiving_channels ):
    for j in range(1,100):
        sending = [s_c.send(5) for s_c in sending_channels]
        receiving = [r_c.receive() for r_c in receiving_channels]
        yield env.select(*sending,*receiving)

def M3(env, s_c ):
    for j in range(1,100):
        send1 = s_c.send(10)
        send2 = s_c.send(11)
        yield env.select(send1,send2)

def M4(env, r_c ):
    for j in range(1,100):
        receive1 = r_c.send(10)
        receive2 = r_c.send(11)
        yield env.select(receive1,receive2)

# =================================
# # Main
# =================================
env = Environment()
Cs = [Channel(env) for z in range(1,5)]  # a channel for each tier, each sending totes

M1s = [env.process(M1(env, Cs, Cs)) for z in range(1,5)]
M2s = [env.process(M2(env, Cs, Cs)) for z in range(1,5)]
M3s = [env.process(M3(env, c)) for c in Cs]
M4s = [env.process(M4(env, c)) for c in Cs]

env.run()
print("simulation has ended")
