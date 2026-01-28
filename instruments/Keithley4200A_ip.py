# -*- coding: utf-8 -*-
"""
Module to interact with a Keithley 4200A-SCS Parameter Analyzer.
Uses pyVISA to communicate with the ethernet device.
Assumes IP address is of the form TCPIP0::<xx>::SOCKET where
<xx> is the IP address (string).

Version 0.5 (2026-01-28)
Daan Wielens - Researcher at ICE/QTM
Daniel Janse van Rensburg - PhD Candidate at ICE
University of Twente
d.h.wielens@utwente.nl
d.h.janse@utwente.nl
"""

import pyvisa

class WrongInstrErr(Exception):
    """
    A connection was established to the instrument, but the instrument
    is not a Keithley 4200A-SCS. Please retry with the correct
    IP address. Make sure that each device has a unique address.
    """
    pass

class Keithley4200A:
    type = 'Keithley 4200A-SCS Parameter Analyzer'

    def __init__(self, IPAddr):
        rm = pyvisa.ResourceManager()
        self.visa = rm.open_resource('TCPIP0::{}::SOCKET'.format(IPAddr))
        self.visa.write_termination = '\0'
        self.visa.read_termination = '\0'
        resp = self.visa.query('*IDN?')
        model = resp.split(',')[1]
        if model not in ['KI4200A', 'MODEL 4200A']:
            raise WrongInstrErr('Expected Keithley KI4200A, got {}'.format(resp))
        self.Icomp = 1.0E-3
        self.Vcomp = 10.0
        self.Icomp_b = 1.0E-3
        self.Vcomp_b = 10.0
        self.IRanges = {
            "auto": 0,
            "1nA": 1,
            "10nA": 2,
            "100nA": 3,
            "1uA": 4,
            "10uA": 5,
            "100uA": 6,
            "1mA": 7,
            "10mA": 8,
            "100mA": 9,
            "1A": 10,
            "1pA": 11,
            "10pA": 12,
            "100pA": 13
        }
        self.VRanges = {
            "auto": 0,
            "20V": 1,
            "200V": 2,
            "200mV": 4,
            "2V": 5
        }
        self.Irange = self.IRanges.get("auto")
        self.Irange_b = self.IRanges.get("auto")
        self.Vrange = self.VRanges.get("auto")
        self.Vrange_b = self.VRanges.get("auto")
        self.Pages = {
            "ChannelDef": "CH",
            "SourceSetup": "SS",
            "MeasSetup": "SM",
            "MeasCont": "MD",
            "UserMode": "US",
            "UserLib": "UL",
        }
        self.page = None
        self.visa.query('DR1')

    def get_iden(self):
        resp = str(self.visa.query('*IDN?'))
        return resp

    def close(self):
        self.visa.close()

    def query(self, val):
        resp = self.visa.query(val)
        return resp

    def pol(self, val):
        self.visa.write(val)
        if self.stb.pol(0):
            resp = self.visa.read()
            return resp

    def set_page(self, val):
        newpage = self.Pages.get(val)
        if newpage is None:
            print(f'Unknown page: {val}; Current page: {self.page}')
            return False
        if newpage == self.page:
            return True
        self.page = newpage
        self.visa.query(self.page)
        return True

    # Normal functions apply to SMU A(1) and _b functions apply to SMU B(2)
    # This keeps 1:1 relationship with 2400 SMU code

    def read_dcv(self):
        self.set_page("UserMode")
        resp = self.visa.query('TV 1')
        resp = float(resp[3:64])
        return resp

    def read_dcv_b(self):
        self.set_page("UserMode")
        resp = self.visa.query('TV 2').strip('\n\r')
        resp = float(resp[3:64])
        return resp

    def write_dcv(self, val):
        fval = float(val)
        if abs(fval) > 210:
            print('Your setpoint is higher than the allowed +/- 210 V and will not be applied.')
        else:
            self.set_page("UserMode")
            self.visa.query('DV1, ' + str(self.Vrange) + ', ' + str(val) + ', ' + str(self.Icomp))

    def write_dcv_b(self, val):
        fval = float(val)
        if abs(fval) > 210:
            print('Your setpoint is higher than the allowed +/- 210 V and will not be applied.')
        else:
            self.set_page("UserMode")
            self.visa.query('DV2, ' + str(self.Vrange_b) + ', ' + str(val) + ', ' + str(self.Icomp_b))

    def read_dci(self):
        self.set_page("UserMode")
        resp = self.visa.query('TI 1')
        resp = float(resp[3:64])
        return resp

    def read_dci_b(self):
        self.set_page("UserMode")
        resp = self.visa.query('TI 2').strip('\n\r')
        resp = float(resp[3:64])
        return resp

    def write_dci(self, val):
        fval = float(val)
        if abs(fval) > 0.1050:
            print('Your setpoint is higher than the allowed +/- 105 mA and will not be applied.')
        else:
            self.set_page("UserMode")
            self.visa.query('DI1, ' + str(self.Irange) + ', ' + str(val) + ', ' + str(self.Vcomp))

    def write_dci_b(self, val):
        fval = float(val)
        if abs(fval) > 0.1050:
            print('Your setpoint is higher than the allowed +/- 105 mA and will not be applied.')
        else:
            self.set_page("UserMode")
            self.visa.query('DI2, ' + str(self.Irange_b) + ', ' + str(val) + ', ' + str(self.Vcomp))

    def read_i(self):
        resp = self.read_dci()
        return resp

    def read_v(self):
        resp = self.read_dcv()
        return resp

    def write_Vrange(self, val):
        inval = self.VRanges.get(val)
        if inval is None:
            print('Unknown voltage range; must be one of:')
            print(self.VRanges)
            print('Defaulting to Autorange!')
            self.Vrange = self.VRanges.get("auto")
        else:
            self.Vrange = inval
            # Could force the range to this value immediately?

    def write_Vrange_b(self, val):
        inval = self.VRanges.get(val)
        if inval is None:
            print('Unknown voltage range; must be one of:')
            print(self.VRanges)
            print('Defaulting to Autorange!')
            self.Vrange_b = self.VRanges.get("auto")
        else:
            self.Vrange_b = inval
            # Could force the range to this value immediately?

    def write_Irange(self, val):
        inval = self.IRanges.get(val)
        if inval is None:
            print('Unknown current range; must be one of:')
            print(self.IRanges)
            print('Defaulting to Autorange!')
            self.Irange = self.IRanges.get("auto")
        else:
            self.Irange = inval
            # Could force the range to this value immediately?

    def write_Irange_b(self, val):
        inval = self.IRanges.get(val)
        if inval is None:
            print('Unknown current range; must be one of:')
            print(self.IRanges)
            print('Defaulting to Autorange!')
            self.Irange_b = self.IRanges.get("auto")
        else:
            self.Irange_b = inval
            # Could force the range to this value immediately?

    # NOTE: This function is not implemented on the 4200A
    def read_output(self):
        return None

    def write_output(self, val):
        if val in [1, 'On', 'ON', 'on']:
            return
        elif val in [0, 'Off', 'OFF', 'off']:
            # NOTE: This is a hack to turn off the devices; there is no alternative to switch the 4200 off
            self.set_page("UserMode")
            self.visa.query("DV1 DV2")
        else:
            print('This is not a valid argument for the Keithley Output command. Your command will be ignored.')

    def read_Vcomplevel(self):
        return self.Vcomp

    def read_Icomplevel(self):
        return self.Icomp

    def write_Vcomplevel(self, val):
        self.Vcomp = val

    def write_Icomplevel(self, val):
        self.Icomp = val

    def read_Vcomplevel_b(self):
        return self.Vcomp_b

    def read_Icomplevel_b(self):
        return self.Icomp_b

    def write_Vcomplevel_b(self, val):
        self.Vcomp_b = val

    def write_Icomplevel_b(self, val):
        self.Icomp_b = val

    def write_integT(self, val):
        self.visa.query('IT' + str(val))