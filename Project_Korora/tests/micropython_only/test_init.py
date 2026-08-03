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
            "SDcard": False,
            "USB": False,
            "PWR": False,
            "Neopixel": False,
        }

        # Define battery voltage
        self._vbatt = AnalogIn(board.BATTERY)

        # Define SPI,I2C,UART
        self.i2c1 = busio.I2C(board.SCL, board.SDA)
        self.spi = board.SPI()
        self.uart = busio.UART(board.TX, board.RX)

        # Define filesystem stuff
        self.test_log_file = "/testlog.txt"

        # Initialize SD card (always init SD before anything else on spi bus)
        try:
            self.init_sd_card()         
            self.test_log_file = "/sd/testlog.txt" # Sets the logging file to use the SD card's storage
            self.hardware["SDcard"] = True
            self.log("SD card init successful")
        except Exception as e:
            self.log(f"[ERROR] SD card init unsuccessful: {e}", force_serial=True)

        # Initialize Neopixel
        try:
            self.init_neopixel()
            self.hardware["Neopixel"] = True
            self.log("Neopixel init successful")
        except Exception as e:
            self.log(f"[ERROR] Neopixel init unsuccessful: {e}", force_serial=True)

        # Initialize USB charger
        try:
            self.init_usb_charger()
            self.hardware["USB"] = True
            self.log("USB charger init successful")
        except Exception as e:
            self.log(f"[ERROR] USB charger init unsuccessful: {e}", force_serial=True)

        # Initialize Power Monitor
        try:
            self.init_pwr_monitor()
            self.hardware["PWR"] = True
            self.log("Power monitor init successful")
        except Exception as e:
            self.log(f"[ERROR] Power monitor init unsuccessful: {e}", force_serial=True)

        # Initialize IMU
        try:
            self.IMU = self.init_imu()
            self.hardware["IMU"] = True
            self.log("IMU init successful")
        except Exception as e:
            self.log(f"IMU init unsuccessful: {e}", force_serial=True)

    def init_sd_card(self) -> bool:
        """
        Attempts to initialise the SD card. If an error occurs, this method throws an exception.
        It is important that the SD card is initialised before anything else on the board.
        """

        # Baud rate depends on the card, 4MHz should be safe
        _sd = sdcardio.SDCard(self.spi, board.SD_CS, baudrate=4000000) # Initialises the SD card
        _vfs = VfsFat(_sd) # Initialises FAT file system on SD card
        mount(_vfs, "/sd") # Mounts the SD card's FAT system at the path "/sd"
        self.fs = _vfs # Sets the satellite's file system 
        sys.path.append("/sd")

        return True


    def init_neopixel(self):
        self.neopixel = neopixel.NeoPixel(
            board.NEOPIXEL, 1, brightness=0.2, pixel_order=neopixel.GRB
        )
        self.neopixel[0] = (0, 0, 0)


    def init_usb_charger(self):
        self.usb = bq25883.BQ25883(self.i2c1)
        self.usb.charging = False
        self.usb.wdt = False
        self.usb.led = False
        self.usb.charging_current = 8  # 400mA
        self.usb_charging = False


    def init_pwr_monitor(self):
        self.pwr = adm1176.ADM1176(self.i2c1)
        self.pwr.sense_resistor = 1


    def init_imu(self):
        self.IMU = bmx160.BMX160_I2C(self.i2c1)
    

    def log(self, msg: str, force_serial: bool = False) -> None:
        """
        Logs a message to the SD card's file system, if the SD card has been mounted.
        If force_serial is true, prints to serial if the SD card's log is not available.
        """

        t = int(time.monotonic())
        if self.hardware["SDcard"]:
            with open(self.logfile, "a+") as f:
                f.write(f"{t}, {msg}\n")
        elif force_serial:
            print(f"{t}, {msg}")


