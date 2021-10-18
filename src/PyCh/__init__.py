#! usr/bin/python3
ver = "0.2"
# ===================================
# import core
# ===================================
from .core.channel import Channel, Communicator, Sender, Receiver
from .core.environment import Environment, process, selected

# ===================================
# import math utilities
# ===================================
from math import *
from dataclasses import dataclass
from numpy import random
import numpy
numpy.seterr(divide='ignore')

# ===================================
# import plot utilities
# ===================================
import matplotlib
from matplotlib import pyplot
matplotlib.use('nbagg')
from .utilities.liveplot import LivePlot, LiveStepPlot

# Finished
print(f"PyCh version {ver} imported succesfully.\n ")