# Copyright (c) 2021 Admiral Instruments

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from serial_communicator import asyncio, logging, SerialCommunicator, serial


class TemperatureController(SerialCommunicator):

    def __init__(self, com_port: str):
        super().__init__(com_port, "Temperature Controller")
        try:
            self.ser = serial.Serial(port=com_port,
                                     baudrate=4800,
                                     bytesize=serial.EIGHTBITS,
                                     timeout=1,
                                     parity=serial.PARITY_NONE,
                                     stopbits=serial.STOPBITS_ONE)
        except IOError as err:
            self.logger.error(f"Error opening serial communication with {self.name}")
            raise err

    async def verify_connection(self) -> bool:
        """
        Requests name from the device to verify that the initial connection with the Temperature Controller was
        made successfully.
        """

        if not self.ser.is_open:
            self.logger.error("Serial connection with Temperature Controller was not opened.")
            return False

        name = await self._send_command("*IDN?")

        if len(name) == 0:
            self.logger.error(f"Error in verifying Temperature Controller with response {name}")
            return False

        return True

    async def set_temperature(self, temperature: float) -> bool:
        """
        Sets the Temperature Controller to the given temperature in Celsius. Returns True if the temperature
        was successfully set and the device responded indicating success, otherwise False.
        """

        response = await self._send_command(f"PRoG>SP1>{temperature}")

        if len(response) == 0:
            self.logger.error("The Temperature Controller failed to acknowledge a change in Temperature setpoint")
            return False
        return True

    async def get_temperature(self) -> float:
        """
        Requests the current temperature reading from the Temperature Controller, the reading is converted into a float
        if possible. If not or no response is given, an IOError is raised to indicate a communication breakdown
        with the Temperature Controller.
        """

        response = await self._send_command("get temperature")

        if len(response) == 0:
            raise IOError("Error requesting temperature from Temperature Controller. There was no response.")

        try:
            return float(response)
        except ValueError as err:
            self.logger.error(f"Error converting {response} from Temperature Controller to string.")
            raise IOError("Error requesting temperature from Temperature Controller. The reading was not a number.")

    async def reset(self) -> bool:
        """
        Puts the Temperature Controller into a neutral state where it no longer applies a set temperature. Returns
        True if the device communicates back that it has successfully reset itself, otherwise False.
        """

        response = await self._send_command("PF30 1")

        if len(response) == 0:
            self.logger.error("The Temperature Controller failed to acknowledge a request to reset its state.")
            return False
        return True

    async def _send_command(self, command: str) -> str:
        """
        Locks the resource and sends ascii text to a serial port and waits until 100 bytes are read back or 1 seconds have passed. Returns
        the bytes read from the serial port in ascii format with new line characters stripped.
        """

        if self.ser is None:
            raise IOError(f"Attempting to write to {self.name} which has no software serial connection.")

        await self.serial_lock.acquire()
        written = bytes(str.join(["*", command, "\r"]), "ascii")
        self.logger.info(f"Wrote {written} to {self.name}")
        self.ser.write(written)
        ret = self.ser.read(100).decode("ascii").rstrip("\n")
        self.ser.flush()
        self.serial_lock.release()
        return ret

