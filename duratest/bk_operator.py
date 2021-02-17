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

from serial_communicator import asyncio, logging, SerialCommunicator


class BKOperator(SerialCommunicator):
    def __init__(self, com_port: str):
        super().__init__(com_port, "BK Power Supply")

    async def verify_connection(self) -> bool:
        """
        Resets the state of the BK Power Supply, waits 5 seconds for the device to reboot, then requests the
        name of the device. If no name response is received, then the function returns False, otherwise True.
        """

        if not self.ser.is_open:
            logging.error("Error opening serial connection with BK Power Supply.")
            return False

        await self._send_command("*RST")
        await asyncio.sleep(5)
        name = await self._send_command("*IDN?")

        if len(name) == 0:
            return False

        await self._send_command("outp on")

        return True

    async def set_current(self, current: float) -> bool:
        """
        Instructs the BK power supply to set the current to the input argument, given in Amperes. Returns True if the
        Power Supply acknowledges its current has been set, otherwise False.
        """

        response = await self._send_command(f"curr {current}")

        if len(response) == 0:
            self.logger.error("Error requesting a change in the current setpoint of the power supply.")
            return False
        return True

    async def get_current(self) -> float:
        """
        Returns the current reading from the BK power supply in Amperes. Raises an IOError if the Power Supply fails to
        give a reading, or if the reading is not a number.
        """

        response = await self._send_command("meas:curr?")

        if (len(response) == 0):
            raise IOError("Error requesting current from Power Supply. There was no response.")

        try:
            return float(response)
        except ValueError as err:
            self.logger.error(f"Error converting current: {response} from Power Supply to string.")
            raise IOError("Error requesting current from Power Supply. The reading was not a number.")

    async def get_voltage(self) -> float:
        """
        Returns the voltage reading from the BK power supply in Voltages. Raises an IOError if the Power Supply fails to
        give a reading, or if the reading is not a number.
        """

        response = await self._send_command("meas:volt?")

        if (len(response) == 0):
            raise IOError("Error requesting voltage from Power Supply. There was no response.")

        try:
            return float(response)
        except ValueError as err:
            self.logger.error(f"Error converting voltage: {response} from Power Supply to string.")
            raise IOError("Error requesting voltage from Power Supply. The reading was not a number.")

    async def set_voltage_limits(self, min_voltage: float, max_voltage: float) -> bool:
        """
        Sets the voltage protection limits. Returns true if the device acknowledges a change in voltage
        limits, otherwise returns false.
        """

        response = await self._send_command("set voltage limit")

        if len(response) == 0:
            self.logger.error("Error requesting a change in the voltage limits of the power supply.")
            return False
        return True

    async def reset(self) -> bool:
        """
        Resets the power supply to put the system it is connected to at rest. Returns True if the Power Supply
        acknowledges it has been reset, otherwise False.
        """

        if (self.ser is None):
            return False

        response = await self._send_command("*RST")

        return len(response) > 0
