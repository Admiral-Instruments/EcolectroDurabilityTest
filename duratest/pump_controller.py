# Copyright (c) 2021 Admiral Instruments

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from serial_communicator import asyncio, logging, SerialCommunicator


class PumpController(SerialCommunicator):

    def __init__(self, com_port: str):
        super().__init__(com_port, "Pump Controller")

    async def verify_connection(self) -> bool:
        """
        Requests name from the device to verify that the initial connection with the Pump Controller was
        made successfully.
        """

        if not self.ser.is_open:
            self.logger.error("Serial connection with Pump Controller was not opened.")
            return False

        name = await self._send_command("*IDN?")

        if len(name) == 0:
            self.logger.error(f"Error in verifying Pump Controller with response {name}")
            return False

        return True

    async def turn_on(self) -> bool:
        """
        Sends a request to the Pump Controller requesting the pump to turn on. Returns True if the pump acknowledges
        a successful pump power on, otherwise returns False.
        """

        response = await self._send_command("on")

        if (len(response) == 0):
            self.logger.error(f"The Pump Controller failed to response to a request to turn on the pump.")
            return False
        return True

    async def turn_off(self) -> bool:
        """
        Sends a request to the Pump Controller requesting the pump to turn off. Returns True if the pump acknowledges
        a successful pump shutoff, otherwise returns False.
        """

        response = await self._send_command("off")

        if (len(response) == 0):
            self.logger.error(f"The Pump Controller failed to response to a request to turn off the pump.")
            return False
        return True

    async def reset(self) -> bool:
        """
        Provided to match function calls given in other SerialCommunicator objects. Calls turn_off
        """

        return self.turn_off()
