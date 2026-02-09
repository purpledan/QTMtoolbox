# -*- coding: utf-8 -*-
"""
Asynchronous measurement script to measure IV sweeps as a function of temperature

Version 0.3 (2026-02-09)
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
cry = CryoLabSP1("192.168.100.55")

# Setup Keithley
sysmod = kei.sysmode(kei)

# Constant settings go here
sysmod.channelsetup(1, 'O', sysmod.chmode.SOURCE_VOLT, sysmod.chfunc.SWEEP)
sysmod.abortoncomp = 1

# Setup temperature steps
Tstart = 300
Tend = 250
Tsteps = 10
Tmax_diff = 1
Tmax_dev = 0.5
Tmax_std = 0.5

Vstart = 0.0
Vend = 10
Vsteps = 2048
Icompliance = 0.02
steps = np.linspace(Tstart, Tend, Tsteps)

name = "Test1"

# Go to temperature, monitor status
for temp_step in steps:
    print(f"Going to {temp_step} K")
    cry.goto(temp_step)
    cry.log()
    cry.log()
    while cry.reached(Tmax_diff, Tmax_dev, Tmax_std) is False:
        cry.log()
        # Check up on other things ?
        debug_ret = cry.stat_debug()
        print(f"Set: {cry.Setp}, Cur: {cry.Temp}, Avg: {debug_ret[0]}, Std: {debug_ret[1]}")
        # Sleep here (sets the polling rate while waiting for temperature setpoint to be reached
        time.sleep(0.5)
    print("Measuring!")
    #Here we assume that the temperature is good
    # We can set up different sweeps for different temperatures, else we can also do this part outside the loop
    sysmod.sweepsetup(1, Vstart, Vend, Vsteps, Icompliance)
    sysmod.measuresetup(1)

    # Set up the file where we will save the IV curves
    file_name = f"{name}_IV_{temp_step:.2f}".replace('.','_')
    file_out = open(file_name, 'w')

    # Upon calling trigger, the device responds after roughly 4 seconds (It is slow when sending a sweep list)
    temperature_result = []
    sysmod.trigger()
    toc = time.time()
    # Waiting loop for the 4200
    while sysmod.busy():
        # Monitor cryolab status while waiting
        temp_ret = cry.read_temperature()
        tic = time.time()
        temperature_result.append((tic - toc, temp_ret))

        print(f"{(tic - toc):.2f}: {temp_ret:} - Busy")
        # this sets the polling rate for the 4200 and cryolab
        time.sleep(0.50)

    # We can now get the data
    result = sysmod.retreve(1)
    # Save the data to a file or something
    file_out.write("time, volt_set, volt_meas, cur_meas\n")
    for i in range(Vsteps):
        file_out.write(f"{result.time_list[i]}, {result.set_list[i]}, {result.volt_list[i]}, {result.curr_list[i]}\n")
    file_out.write("### Temp Log ###\n")
    file_out.write("time, temperature\n")
    for i in range(len(temperature_result)):
        file_out.write(f"{temperature_result[i][0]}, {temperature_result[i][0]}\n")
    file_out.close()
    # Go to next temperature setpoint
    print("Done with setpoint")

# Done with experiment
print("Done")