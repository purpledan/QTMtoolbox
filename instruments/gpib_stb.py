# -*- coding: utf-8 -*-
"""
Helper module for using GPIB Status byte to poll instruments

Version 0.1 (2026-01-27)
Daan Wielens - Researcher at ICE/QTM
Daniel Janse van Rensburg - PhD Candidate at ICE
University of Twente
d.h.wielens@utwente.nl
d.h.janse@utwente.nl
"""
import time

class gpib_stb:
    def __init__(self):
        self.stb = 0

        # Polling rate i.e. number of times per second
        self.pol_rate = 60
        # Timeout value in ms
        self.timeout = 1000

        self.get = None

    def read(self, bit):
        if self.get:
            self.stb = self.get()

        if self.stb & (1 << bit) != 0:
            return True
        return False

    def pol(self, bit):
        ns_start = time.time_ns()
        while self.read(bit) is not True:
            ns_waited = time.time_ns() - ns_start
            if ns_waited >= (self.timeout * 1E6):
                return False
            time.sleep(1/self.pol_rate)
        return True




