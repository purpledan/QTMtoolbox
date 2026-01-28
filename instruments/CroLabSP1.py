# -*- coding: utf-8 -*-
"""
Module to interact with a Kryos CryoLab SP1 fridge.
Uses pyVISA to communicate with the ethernet device.
Assumes IP address is of the form TCPIP0::<xx>::SOCKET where
<xx> is the IP address (string).

Version 0.1 (2026-01-28)
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
        self.visa = rm.open_resource('TCPIP0::{}::5041::SOCKET'.format(IPAddr))
        self.visa.write_termination = '\r\n'
        self.visa.read_termination = '\r\n\r\n' # This is a bug on their side; manual says it should be just \r\n
        resp = self.visa.query('STATUS')
        model = resp.split(':')[0]
        if model not in ['STATUS', '|']:
            raise WrongInstrErr('Expected CryoLab, got {}'.format(resp))

        self.Setp = -0.0
        self.Temp = -0.0
        self.HPow = -0.0
        self.BPres = -0.0
        self.LPres = -0.0
        self.Vac = -0.0

    def read_status(self):
        retval = self.visa.query('SENSORS')
        status = retval.split(':')[1].split('|')
        self.Setp = float(status[1])
        self.Temp = float(status[2])
        self.HPow = float(status[3])
        self.BPres = float(status[4])
        self.LPres = float(status[5])
        self.Vac = float(status[6])

    def write_Setp(self, temperature):
        retval = self.visa.query('SETPOINT: {:.2f}'.format(temperature))
        status = retval.split(':')[1]
        if status is 'OK':
            return True
        return False

    def read_temperature(self):
        self.read_status()
        return self.Temp