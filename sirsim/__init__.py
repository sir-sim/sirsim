"""
Sirsim
=====

Sirsim (Social Innovation and Resilience Simulation) is a package for 
doing large-scale social decision modelling in Python.

The source code repository for this package is found at
https://www.github.com/sir-sim/sirsim.
"""

import logging

from .version import version as __version__

# Sirsim namespace (API)
#from .base import Process
#from .config import Config
from .connection import Connection
from .ensemble import Ensemble
from .node import Node
from .agents import (
    LIF, LIFRate)
#from .agents import (
#    AdaptiveLIF, AdaptiveLIFRate, Direct, Izhikevich, LIF, LIFRate,
#    RectifiedLinear, Sigmoid, SpikingRectifiedLinear)
from .network import Network
from .learning_rules import PES #, BCM, Oja, Voja
###from .params import Default
from .probe import Probe
###from .rc import rc, RC_DEFAULTS
from .simulator import Simulator
#from .synapses import Alpha, LinearFilter, Lowpass, Triangle
#from .transforms import Dense, Convolution
#####from .utils.logging import log
###from . import dists, exceptions, networks, presets, processes, spa, utils

# logger = logging.getLogger(__name__)
# try:
#     # Prevent output if no handler set
#     logger.addHandler(logging.NullHandler())
# except AttributeError:
#     pass

__copyright__ = "2019, Sirsim"
__license__ = "Free for non-commercial use; see LICENSE"
