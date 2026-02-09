# -*- coding: utf-8 -*-
"""
Adds a ring buffer for logging measurements

This implementation is based on the following online resource:
https://www.oreilly.com/library/view/python-cookbook/0596001673/ch05s19.html
Accessed 2026-02-05

Version 0.1 (2026-02-05)
Daniel Janse van Rensburg - PhD Candidate at ICE
University of Twente
d.h.janse@utwente.nl
"""

import statistics as stat
from math import inf


class RingBuffer:
    def __init__(self, size_max):
        self.max = size_max
        self.data = []

    class __Full:
        def append(self, x):
            self.data[self.cur] = x
            self.cur = (self.cur+1) % self.max

        def get(self):
            return self.data[self.cur:] + self.data[:self.cur]

    def append(self, x):
        self.data.append(x)
        if len(self.data) == self.max:
            self.cur = 0
            self.__class__ = self.__Full

    def get(self):
        return self.data
