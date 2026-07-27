import sys
import time

# Common CircuitPython Libs
from os import chdir, mkdir, stat

import adm1176  # Power Monitor
import bmx160  # IMU

# Common CircuitPython Libs
import board
import bq25883  # USB Charger
import busio
import digitalio
import microcontroller
import neopixel  # RGB LED
import pwmio

# Hardware Specific Libs
import pycubed_rfm9x  # Radio
import sdcardio
from analogio import AnalogIn
from bitflags import bitFlag, multiBitFlag

# multiByte may also be useful
from micropython import const
from storage import VfsFat, mount, umount

# listdir and statvfs may also be useful


# Commented while unused to satisfy preconfig checks.
# import tasko


# NVM register numbers
_BOOTCNT = const(0)
_VBUSRST = const(6)
_STATECNT = const(7)
_TOUTS = const(9)
_GSRSP = const(10)
_ICHRG = const(11)
_FLAG = const(16)

SEND_BUFF = bytearray(252)


# General NVM counters
c_boot = multiBitFlag(register=_BOOTCNT, lowest_bit=0, num_bits=8)
c_vbusrst = multiBitFlag(register=_VBUSRST, lowest_bit=0, num_bits=8)
c_state_err = multiBitFlag(register=_STATECNT, lowest_bit=0, num_bits=8)
c_gs_resp = multiBitFlag(register=_GSRSP, lowest_bit=0, num_bits=8)
c_ichrg = multiBitFlag(register=_ICHRG, lowest_bit=0, num_bits=8)

# Define NVM flags
f_lowbatt = bitFlag(register=_FLAG, bit=0)
f_solar = bitFlag(register=_FLAG, bit=1)
f_gpson = bitFlag(register=_FLAG, bit=2)
f_lowbtout = bitFlag(register=_FLAG, bit=3)
f_gpsfix = bitFlag(register=_FLAG, bit=4)
f_shtdwn = bitFlag(register=_FLAG, bit=5)

# Initialise all the things we expect
# Run through a series of health checks for each component
# If we receive unknown/unexpected error, we know we have a problem even further down the stack

# Mock satellite class
# Note that the MockSatellite is not actually a mock
# Note that the MockSatellite is not actually a mock
# Note that the MockSatellite is not actually a mock
class MockSatellite:

    # General NVM counters
    c_boot = multiBitFlag(register=_BOOTCNT, lowest_bit=0, num_bits=8)
    c_vbusrst = multiBitFlag(register=_VBUSRST, lowest_bit=0, num_bits=8)
    c_state_err = multiBitFlag(register=_STATECNT, lowest_bit=0, num_bits=8)
    c_gs_resp = multiBitFlag(register=_GSRSP, lowest_bit=0, num_bits=8)
    c_ichrg = multiBitFlag(register=_ICHRG, lowest_bit=0, num_bits=8)

    # Define NVM flags
    f_lowbatt = bitFlag(register=_FLAG, bit=0)
    f_solar = bitFlag(register=_FLAG, bit=1)
    f_gpson = bitFlag(register=_FLAG, bit=2)
    f_lowbtout = bitFlag(register=_FLAG, bit=3)
    f_gpsfix = bitFlag(register=_FLAG, bit=4)
    f_shtdwn = bitFlag(register=_FLAG, bit=5)

    def __init__(self):
        """
        Big init routine as the whole board is brought up.
        """
        self.BOOTTIME = const(time.monotonic())
        self.data_cache = {}
        self.filenumbers = {}
        self.vlowbatt = 6.0
        self.send_buff = memoryview(SEND_BUFF)
        self.debug = True
        self.micro = microcontroller
        self.hardware = {
            "IMU": False,
            "Radio1": False,
            "Radio2": False,
            "SDcard": False,
            "GPS": False,
            "WDT": False,
            "USB": False,
            "PWR": False,
        }

        # Define burn wires
        self._relayA = digitalio.DigitalInOut(board.RELAY_A)
        self._relayA.switch_to_output(drive_mode=digitalio.DriveMode.OPEN_DRAIN)
        self._resetReg = digitalio.DigitalInOut(board.VBUS_RST)
        self._resetReg.switch_to_output(drive_mode=digitalio.DriveMode.OPEN_DRAIN)

        # Define battery voltage
        self._vbatt = AnalogIn(board.BATTERY)

        # Define MPPT charge current measurement
        self._ichrg = AnalogIn(board.L1PROG)
        self._chrg = digitalio.DigitalInOut(board.CHRG)
        self._chrg.switch_to_input()

        # Define SPI,I2C,UART
        self.i2c1 = busio.I2C(board.SCL, board.SDA)
        self.spi = board.SPI()
        self.uart = busio.UART(board.TX, board.RX)

        # Define GPS
        # self.en_gps = digitalio.DigitalInOut(board.EN_GPS)
        # self.en_gps.switch_to_output()

        # Define filesystem stuff
        self.test_log_file = "/testlog.txt"

        # Define radio
        #_rf_cs1 = digitalio.DigitalInOut(board.RF1_CS)
        #_rf_rst1 = digitalio.DigitalInOut(board.RF1_RST)
        #self.enable_rf = digitalio.DigitalInOut(board.EN_RF)
        #self.radio1_DIO0 = digitalio.DigitalInOut(board.RF1_IO0)
        # self.enable_rf.switch_to_output(value=False) # if U21
        #self.enable_rf.switch_to_output(value=True)  # if U7
        #_rf_cs1.switch_to_output(value=True)
        #_rf_rst1.switch_to_output(value=True)
        #self.radio1_DIO0.switch_to_input()

        # Initialize SD card (always init SD before anything else on spi bus)
        try:
            # Baud rate depends on the card, 4MHz should be safe
            _sd = sdcardio.SDCard(self.spi, board.SD_CS, baudrate=4000000)
            _vfs = VfsFat(_sd)
            mount(_vfs, "/sd")
            self.fs = _vfs
            sys.path.append("/sd")
            self.hardware["SDcard"] = True
            self.logfile = "/sd/log.txt"
        except Exception as e:
            if self.debug:
                print("[ERROR][SD Card]", e)

        # Initialize Neopixel
        try:
            self.neopixel = neopixel.NeoPixel(
                board.NEOPIXEL, 1, brightness=0.2, pixel_order=neopixel.GRB
            )
            self.neopixel[0] = (0, 0, 0)
            self.hardware["Neopixel"] = True
        except Exception as e:
            if self.debug:
                print("[WARNING][Neopixel]", e)

        # Initialize USB charger
        try:
            self.usb = bq25883.BQ25883(self.i2c1)
            self.usb.charging = False
            self.usb.wdt = False
            self.usb.led = False
            self.usb.charging_current = 8  # 400mA
            self.usb_charging = False
            self.hardware["USB"] = True
        except Exception as e:
            if self.debug:
                print("[ERROR][USB Charger]", e)

        # Initialize Power Monitor
        try:
            self.pwr = adm1176.ADM1176(self.i2c1)
            self.pwr.sense_resistor = 1
            self.hardware["PWR"] = True
        except Exception as e:
            if self.debug:
                print("[ERROR][Power Monitor]", e)

        # Initialize IMU
        try:
            self.IMU = bmx160.BMX160_I2C(self.i2c1)
            self.hardware["IMU"] = True
        except Exception as e:
            if self.debug:
                print("[ERROR][IMU]", e)
