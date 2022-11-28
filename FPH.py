from VISAInstrument import VISAInstrument
from datetime import datetime


class FPH(VISAInstrument):

    def print_info(self):
        # print instrument info
        info = self.query("*IDN?").strip().split(",")
        print(datetime.now(), info[0], info[1])
        print(datetime.now(), "serial number:", info[2])
        print(datetime.now(), "firmware revision:", info[3])

    def set_span(self):
        self.write("FREQ:SPAN:AUTO ON")

    def set_span(self, span: str):
        self.write("FREQ:SPAN " + span)
        res = self.query("FREQ:SPAN?")
        print(datetime.now(), "SPAN set:", res.strip(), "Hz")

    def set_step(self, step: str):
        self.write("FREQ:CENT:STEP " + step)
        res = self.query("FREQ:CENT:STEP?")
        print(datetime.now(), "STEP set:", res.strip(), "Hz")

    def set_RBW(self, step: str):
        # resolution bandwidth
        self.write("BAND " + step)
        res = self.query("BAND?")
        print(datetime.now(), "BAND set:", res.strip(), "Hz")

    def set_center(self, center: str, log=False):
        self.write("FREQ:CENT " + center)
        if log:
            res = self.query("FREQ:CENT?")
            print(datetime.now(), "CENTer set:", res.strip(), "Hz")

    def set_sweep_time(self, time: str):
        self.write("SWE:TIME " + time)
        res = self.query("SWE:TIME?")
        print(datetime.now(), "SWEep TIME set:", res.strip(), "s")
