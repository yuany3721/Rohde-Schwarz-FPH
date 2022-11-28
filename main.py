# -*- coding: utf-8 -*-

import pyvisa as visa
from FPH import FPH
from Logger import Logger
import sys
import time
import getopt
import csv
from Timer import Timer
from datetime import datetime

# communication timeout with ITC4001 (ms)
TIMEOUT = 10000
# waiting time for finding start freq center (s)
WAITING_TIME = 5
# sweep interval (ms)
INTERVAL = 500
# whether save sweep log
SWEEP_LOG = True
# whether reset the instrument while initialization
RESET = True


def noe(num: str) -> str:
    if "e" in num:
        i = num.index("e")
        e = int(num[i+2:])
        numf = float(num[:i]) * pow(10, e)
        return str(numf)
    return num


def sweep(instrument: FPH) -> None:

    def get_peak():
        # start sweep
        instrument.write("INIT:CONT OFF")
        # wait for sweep
        instrument.write("INIT;*WAI")
        instrument.write("CALC:MARK1:MAX")
        peak = instrument.query("CALC:MARK:X?").strip()
        if SWEEP_LOG:
            with open(str(datetime.now()).split(" ")[0] + ".csv", "a", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([str(datetime.now()), noe(peak)])
        instrument.set_center(peak)

    instrument.set_center("5GHz", True)
    instrument.set_span("10GHz")
    # instrument.set_RBW("100kHz")
    # instrument.set_step("100MHz")
    # instrument.set_sweep_time(str(WAITING_TIME * 500) + "ms")

    # find peak
    instrument.write("INIT:CONT OFF")
    instrument.write("CALC:MARK1 ON")
    instrument.write("INIT;*WAI")
    time.sleep(WAITING_TIME*0.6)
    instrument.write("CALC:MARK1:MAX")
    time.sleep(2)
    peak = instrument.query("CALC:MARK:X?").strip()
    print(datetime.now(), "find peak:", peak, "Hz")

    # adjust resolution
    instrument.set_center(peak, True)
    instrument.set_span("100MHz")
    # instrument.set_RBW("300kHz")
    # instrument.set_step("100kHz")
    # instrument.set_sweep_time(str(INTERVAL-50) + "ms")

    print(datetime.now(), "start sweep")
    timer = Timer(get_peak, INTERVAL)
    timer.start()


if __name__ == "__main__":

    sys.stdout = Logger()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hlr:c:q:", ["help", "list", "resource=", "command=", "query="])
    except getopt.GetoptError:
        print("wrong args")
        print("Please running with -h, --help for using guidance")
        exit(2)

    if len(opts) < 1:
        print("Please running with -h, --help for using guidance")
        exit(0)

    visaResource = None
    tunningFile = None
    command = None
    query = None
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("-l, --list\n\tlist all visa resources")
            print("-r A::B::C, --resource A::B::C\n\tconnect Spectrum FPH at A::B::C")
            print("-c YOURCOMMAND, --command YOURCOMMAND\n\trun YOURCOMMAND command")
            exit(0)
        elif opt in ("-l", "--list"):
            print(visa.ResourceManager().list_resources())
            exit(0)
        elif opt in ("-r", "--resource"):
            visaResource = arg
        elif opt in ("-c", "--command"):
            command = arg
        elif opt in ("-q", "--query"):
            query = arg

    if visaResource == None:
        print("no resource input")
        print("Please running with -h, --help for using guidance")
        if command == None:
            exit(0)

    if command == None:
        print(datetime.now(), "Preparing with", INTERVAL, "ms interval at", visaResource)

    try:
        instrument = FPH(visaResource, TIMEOUT, RESET)
    except BaseException as e:
        print(e)
        exit(0)

    if not (command == None):
        print(datetime.now(), "excuting command:", command)
        print(instrument.command(command))
        exit(0)
    elif not (query == None):
        print(datetime.now(), "excuting query:", query)
        print(instrument.query(query))
        exit(0)

    sweep(instrument)
