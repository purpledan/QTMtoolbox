# -*- coding: utf-8 -*-
"""
Module to interact with a Keithley 4200A-SCS Parameter Analyzer.
Uses pyVISA to communicate with the ethernet device.
Assumes IP address is of the form TCPIP0::<xx>::SOCKET where
<xx> is the IP address (string).

Version 0.8 (2026-02-03)
Daan Wielens - Researcher at ICE/QTM
Daniel Janse van Rensburg - PhD Candidate at ICE
University of Twente
d.h.wielens@utwente.nl
d.h.janse@utwente.nl
"""

import pyvisa
import numpy as np
from enum import Enum


class WrongInstrErr(Exception):
    """
    A connection was established to the instrument, but the instrument
    is not a Keithley 4200A-SCS. Please retry with the correct
    IP address. Make sure that each device has a unique address.
    """
    pass

class Keithley4200A:
    type = 'Keithley 4200A-SCS Parameter Analyzer'

    class Pages(Enum):
        CHANNEL_SET = "DE"
        SOURCE_SET = "SS"
        MEAS_SET = "SM"
        MEAS_CON = "MD"
        USER = "US"
        USER_LIB = "UL"

    def __init__(self, IPAddr):
        rm = pyvisa.ResourceManager()
        self.visa = rm.open_resource('TCPIP0::{}::1225::SOCKET'.format(IPAddr))
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

        self.page = None
        self.holdt = 0
        self.delayt = 0

        self.visa.query('DR1')

    def close(self):
        self.visa.close()

    def query(self, val):
        resp = self.visa.query(val)
        return resp

    def pol(self, bit):
        resp = int(self.query('SP'))
        if resp & (1 << bit) != 0:
            return True
        return False

    def set_page(self, page):
        if page.value == self.page:
            return True
        self.page = page.value
        self.visa.query(self.page)
        return True

    # Normal functions apply to SMU A(1) and _b functions apply to SMU B(2)
    # This keeps 1:1 relationship with 2400 SMU code

    def read_dcv(self):
        self.set_page(self.Pages.USER)
        resp = self.visa.query('TV 1')
        resp = float(resp[3:64])
        return resp

    def read_dcv_b(self):
        self.set_page(self.Pages.USER)
        resp = self.visa.query('TV 2')
        resp = float(resp[3:64])
        return resp

    def write_dcv(self, val):
        fval = float(val)
        if abs(fval) > 210:
            print('Your setpoint is higher than the allowed +/- 210 V and will not be applied.')
        else:
            self.set_page(self.Pages.USER)
            self.visa.query('DV1, ' + str(self.Vrange) + ', ' + str(val) + ', ' + str(self.Icomp))

    def write_dcv_b(self, val):
        fval = float(val)
        if abs(fval) > 210:
            print('Your setpoint is higher than the allowed +/- 210 V and will not be applied.')
        else:
            self.set_page(self.Pages.USER)
            self.visa.query('DV2, ' + str(self.Vrange_b) + ', ' + str(val) + ', ' + str(self.Icomp_b))

    def read_dci(self):
        self.set_page(self.Pages.USER)
        resp = self.visa.query('TI 1')
        resp = float(resp[3:64])
        return resp

    def read_dci_b(self):
        self.set_page(self.Pages.USER)
        resp = self.visa.query('TI 2')
        resp = float(resp[3:64])
        return resp

    def write_dci(self, val):
        fval = float(val)
        if abs(fval) > 0.1050:
            print('Your setpoint is higher than the allowed +/- 105 mA and will not be applied.')
        else:
            self.set_page(self.Pages.USER)
            self.visa.query('DI1, ' + str(self.Irange) + ', ' + str(val) + ', ' + str(self.Vcomp))

    def write_dci_b(self, val):
        fval = float(val)
        if abs(fval) > 0.1050:
            print('Your setpoint is higher than the allowed +/- 105 mA and will not be applied.')
        else:
            self.set_page(self.Pages.USER)
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
            self.set_page(self.Pages.USER)
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

    def set_holdtime(self, val):
        self.holdt = val

    def set_delaytime(self, val):
        self.delayt = val

    def bufferclear(self):
        self.visa.query('BC')

#   System Mode commands; See the Keithley Programing manual for an overview
    class sysmode:
        class chmode(Enum):
            SOURCE_VOLT = 1
            SOURCE_CURR = 2
            SOURCE_COMM = 3

        class chfunc(Enum):
            SWEEP = 1
            STEP = 2
            CONST = 3
            SOURCE = 4

        def __init__(self, device):
            self.dev: Keithley4200A = device
            self.channelA = None
            self.channelB = None
            self.delaytime = 0.0
            self.holdtime = 0.0
            self.autooff = 1
            self.waittime = 0.0
            self.between = 0.01
            self.integration = 2
            self.abortoncomp = 0

            self.sweeplist = None


        def channelsetup(self, channel: int, name: str, mode, func):
            self.dev.set_page(self.dev.Pages.CHANNEL_SET)
            self.dev.query("CH{chan}, '{chan_name}V{chan}', '{chan_name}I{chan}', {chan_mode}, {chan_func}".format(chan = channel, chan_name = name, chan_mode = mode.value, chan_func = func.value))
            if channel == 1:
                self.channelA = (channel, name, mode.value, func.value)
            if channel == 2:
                self.channelB = (channel, name, mode.value, func.value)

        def sweepsetup(self, channel: int, start: float, end: float, npoints: int, compliance: float):
            assert npoints <= 4096 # Limit for the 4200A

            sweep_string = ""
            sweep = np.linspace(start, end, npoints)
            self.sweeplist = np.copy(sweep)
            for step in sweep:
                sweep_string = sweep_string + ", {}".format(float(step))

            self.dev.set_page(self.dev.Pages.SOURCE_SET)
            mode = None
            chan_set = None
            if channel == 1:
                chan_set = self.channelA
            else:
                chan_set = self.channelB

            if chan_set[2] == self.chmode.SOURCE_VOLT.value:
                mode = 'VL'
            elif chan_set[2] == self.chmode.SOURCE_CURR.value:
                mode = 'IL'

            self.dev.query('{chan_mode}{chan_num}, 1, {compl}'.format(chan_mode = mode, chan_num = chan_set[0], compl = compliance) + sweep_string)

            self.dev.query('DT {:.3f}'.format(self.delaytime))
            self.dev.query('HT {:.1f}'.format(self.holdtime))
            self.dev.query('ST {chan_num}, {set}'.format(chan_num = chan_set[0], set = self.autooff))
            self.dev.query('EC {}'.format(self.abortoncomp))

        def measuresetup(self, channel):
            self.dev.set_page(self.dev.Pages.MEAS_SET)
            self.dev.query('DM2')
            self.dev.query('IN {:.2f}'.format(self.between))
            self.dev.query('WT {:.3f}'.format(self.waittime))
            self.dev.write_integT(self.integration)
            chan_set = None
            if channel == 1:
                chan_set = self.channelA
            else:
                chan_set = self.channelB
            self.dev.query("LI '{chan_name}V{chan}', '{chan_name}I{chan}'".format(chan_name = chan_set[1], chan = chan_set[0]))

        def rangesetup(self, channel, source_range):
            chan_set = None
            if channel == 1:
                chan_set = self.channelA
            else:
                chan_set = self.channelB
            self.dev.query('SR {chan_num}, {range_set}'.format(chan_num = chan_set[0], range_set = source_range))

        def trigger(self):
            self.dev.set_page(self.dev.Pages.MEAS_CON)
            self.dev.query("ME1")

        def retreve(self, channel):
            chan_set = None
            if channel == 1:
                chan_set = self.channelA
            else:
                chan_set = self.channelB

            status: str = self.dev.query("DO 'CH{}S'".format(chan_set[0]))
            status = status.split(',')

            timestamps: str = self.dev.query("DO 'CH{}T'".format(chan_set[0]))
            timestamps = timestamps.split(',')

            voltages: str = self.dev.query("DO '{chan_name}V{chan}'".format(chan_name = chan_set[1], chan = chan_set[0]))
            voltages = voltages.split(',')

            currents: str = self.dev.query("DO '{chan_name}I{chan}'".format(chan_name = chan_set[1], chan = chan_set[0]))
            currents = currents.split(',')

            return status, timestamps, voltages, currents

        def busy(self):
            return  self.dev.pol(4)

        def abort(self):
            self.dev.set_page(self.dev.Pages.MEAS_CON)
            self.dev.query("ME4")




