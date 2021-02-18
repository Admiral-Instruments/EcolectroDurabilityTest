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

import asyncio
import subprocess
import logging


class PumpController:

    def __init__(self, serial_number: str):
        self.serial_lock = asyncio.Lock()
        self.serial_number = serial_number
        self.logger = logging.getLogger("serial")

    async def turn_on(self) -> bool:
        """
        Sends a request to the Pump Controller requesting the pump to turn on. Returns True if the pump acknowledges
        a successful pump power on, otherwise returns False.
        """

        await self._send_command("open")

        return True

    async def turn_off(self) -> bool:
        """
        Sends a request to the Pump Controller requesting the pump to turn off. Returns True if the pump acknowledges
        a successful pump shutoff, otherwise returns False.
        """

        await self._send_command("close")

        return True

    async def _send_command(self, command: str) -> bool:

        output = subprocess.run(["pumpcontroller.exe", self.serial_number, command, "01"])
        self.logger.info(f"Wrote \"{command}\" to Pump controller")

        if output.returncode != 0:
            self.logger.warning(f"The pump controller failed with exit code {output.returncode} for command: {command}")
            raise IOError(f"The Pump Control returned a failed exit code for command {command}")

    async def reset(self) -> bool:
        """
        Provided to match function calls given in other SerialCommunicator objects. Calls turn_off
        """

        return await self.turn_off()
