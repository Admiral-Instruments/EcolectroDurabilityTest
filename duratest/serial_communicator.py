import asyncio
import serial
import logging


class SerialCommunicator:
    def __init__(self, com_port: str, name: str):
        self.logger = logging.getLogger("serial")
        self.com_port = com_port
        self.name = name
        self.serial_lock = asyncio.Lock()
        try:
            self.ser = serial.Serial(port=com_port,
                                     baudrate=9600,
                                     bytesize=serial.EIGHTBITS,
                                     timeout=1,
                                     parity=serial.PARITY_NONE,
                                     stopbits=serial.STOPBITS_ONE)
        except IOError as err:
            self.logger.error(f"Error opening serial communication with {name}")
            raise err

    async def verify_connection(self) -> bool:
        raise NotImplementedError("Connection must be verified before proceeding")

    async def _send_command(self, command: str) -> str:
        """
        Locks the resource and sends ascii text to a serial port and waits until 100 bytes are read back or 1 seconds have passed. Returns
        the bytes read from the serial port in ascii format with new line characters stripped.
        """

        if(self.ser is None):
            raise IOError(f"Attempting to write to {self.name} which has no software serial connection.")

        await self.serial_lock.acquire()
        written = bytes(str().join((command, "\r")), "ascii")
        self.logger.info(f"Wrote {written} to {self.name}")
        self.ser.write(written)
        ret = self.ser.read(100).decode("ascii").rstrip("\n")
        self.ser.flush()
        self.serial_lock.release()
        return ret
