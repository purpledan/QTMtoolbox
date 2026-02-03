# -*- coding: utf-8 -*-
"""
Asynchronous measurement script to measure IV sweeps as a function of temperature

Version 0.2 (2026-02-03)
Daniel Janse van Rensburg - PhD Candidate at ICE
University of Twente
d.h.janse@utwente.nl
"""


import numpy as np
import time

# Import device definitions
from instruments.curtime import *
from instruments.Keithley4200A import *
from instruments.CroLabSP1 import *

# Connect to devices
ct = curtime()
kei = Keithley4200A("192.168.10.42")
#cry = CryoLabSP1("192.169.100.55")

# Setup Keithley
sysmod = kei.sysmode(kei)
sysmod.channelsetup(1, 'O', sysmod.chmode.SOURCE_VOLT, sysmod.chfunc.SWEEP)

sysmod.abortoncomp = 1

sysmod.sweepsetup(1, 0.0, 10, 2048, 0.02)
sysmod.measuresetup(1)
sysmod.trigger()

while sysmod.busy():
    print("Waiting")
    
    
    time.sleep(0.50)

result = sysmod.retreve(1)

# Save the data to a file