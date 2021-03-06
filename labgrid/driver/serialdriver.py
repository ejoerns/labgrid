import logging

import attr
import serial
from pexpect import TIMEOUT

from ..factory import target_factory
from ..protocol import ConsoleProtocol
from ..resource import SerialPort
from .common import Driver
from .consoleexpectmixin import ConsoleExpectMixin


@target_factory.reg_driver
@attr.s
class SerialDriver(ConsoleExpectMixin, Driver, ConsoleProtocol):
    """
    Driver implementing the ConsoleProtocol interface over a SerialPort connection
    """
    bindings = {"port": SerialPort, }

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        self.serial = serial.Serial(
        )  #pylint: disable=attribute-defined-outside-init
        self.status = 0  #pylint: disable=attribute-defined-outside-init
        self.logger = logging.getLogger("{}({})".format(self, self.target))

    def on_activate(self):
        self.serial.port = self.port.port
        self.serial.baudrate = self.port.speed
        self.open()

    def _read(self, size: int=1, timeout: int=0):
        """
        Reads 'size' bytes from the serialport

        Keyword Arguments:
        size -- amount of bytes to read, defaults to 1024
        """
        self.logger.debug("Reading %s bytes with %s timeout", size, timeout)
        self.serial.timeout = timeout
        res = self.serial.read(size)
        self.logger.debug("Read bytes (%s) or timeout reached", res)
        if not res:
            raise TIMEOUT("Timeout exceeded")
        return res

    def _write(self, data: bytes):
        """
        Writes 'data' to the serialport

        Arguments:
        data -- data to write, must be bytes
        """
        self.logger.debug("Write bytes (%s)", data)
        return self.serial.write(data)

    def open(self):
        """Opens the serialport, does nothing if it is already closed"""
        if not self.status:
            self.serial.open()
            self.status = 1

    def close(self):
        """Closes the serialport, does nothing if it is already closed"""
        if self.status:
            self.serial.close()
            self.status = 0
