#! usr/bin/python3
ver = "20210927"
print(f"PyChi version {ver} imported succesfully.\n ")
from .core.channel import Channel
from .core.environment import Environment, process, selected

from math import *
from dataclasses import dataclass
from numpy import random

import numpy
numpy.seterr(divide='ignore')
import matplotlib.pyplot as plt
