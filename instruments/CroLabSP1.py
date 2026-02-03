# -*- coding: utf-8 -*-
"""
Module to interact with a Kryos CryoLab SP1 fridge.
Uses pyVISA to communicate with the ethernet device.
Assumes IP address is of the form TCPIP0::<xx>::SOCKET where
<xx> is the IP address (string).

Version 0.2 (2026-01-29)
Daniel Janse van Rensburg - PhD Candidate at ICE
University of Twente
d.h.janse@utwente.nl
"""

import pyvisa


class WrongInstrErr(Exception):
    """
    A connection was established to the instrument, but the instrument
    is not a CryoLab SP1. Please retry with the correct
    IP address.
    """
    pass


class CryoLabSP1:
    type = 'Kryos CryoLab SP1'

    def __init__(self, IPAddr):
        rm = pyvisa.ResourceManager()
        self.visa = rm.open_resource('TCPIP0::{}::5046::SOCKET'.format(IPAddr))
        self.visa.write_termination = '\r\n'
        self.visa.read_termination = '\r\n'
        resp = self.query('STATUS')
        model = resp.split(':')[0]
        if model not in ['STATUS', '|']:
            raise WrongInstrErr('Expected CryoLab, got {}'.format(resp))

        self.Setp = -0.0
        self.Temp = -0.0
        self.HPow = -0.0
        self.BPres = -0.0
        self.LPres = -0.0
        self.Vac = -0.0

    def query(self, val):
        retval = self.visa.query(val)
        self.visa.read()  # The server sends an extra \r\n so we read and discard
        return retval

    def read_status(self):
        retval = self.query('SENSORS')
        status = retval.split(':')[1].split('|')
        self.Setp = float(status[0])
        self.Temp = float(status[1])
        self.HPow = float(status[2])
        self.BPres = float(status[3])
        self.LPres = float(status[4])
        self.Vac = float(status[5])

    def write_temperature(self, temperature):
        retval = self.query('SETPOINT: {:.2f}'.format(temperature))
        status = retval.split(':')[1]
        if status == 'OK':
            return True
        return False

    def read_temperature(self):
        self.read_status()
        return self.Temp

    def read_setpoint(self):
        self.read_status()
        return self.Setp

    def read_vacuum(self):
        self.read_status()
        return self.Vac
