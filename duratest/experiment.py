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

import json
import asyncio
import logging

from bk_operator import BKOperator
from pump_controller import PumpController
from temperature_controller import TemperatureController
from os import path, makedirs


class Experiment:
    def __init__(self):
        with open("experiment.json") as f:
            data = json.load(f)

        self.sampling_rate = data["sampling-rate"]
        self.duration = data["duration"]
        self.save_path = data["save-path"]
        save_dir = path.dirname(self.save_path)

        if not path.exists(save_dir):
            makedirs(save_dir)

        # save log in same directory that .csv data is stored
        logging.basicConfig(filename=path.join(save_dir, "experiment.log"),
                            level=logging.DEBUG, format="%(asctime)s %(message)s")

        self.bk_options = data["Power-Supply-options"]
        self.pump_options = data["Pump-Controller-options"]
        self.temperature_options = data["Temperature-Controller-options"]

        # these three are not assigned until run_experiment is called publicly (privately, they are assigned in
        # their getter methods)
        self.bk_operator = None
        self.temp_controller = None
        self.pump_controller = None

        # this is overwritten and used to measure dV for successive voltage measurements
        self.previous_voltage = None

    async def run_experiment(self):
        """
        Runs a simple loop that will execute for at least the duration given in experiment.json. Depending on how long
        it takes to get readings from each device, the duration of the experiment may be longer than experiment.json. (I
        estimate it would be bounded above by about duration + duration/sampling_rate)
        """

        await self._start_experiment()
        while self.duration > 0:
            await self._process_readings()
            self.duration -= self.sampling_rate
            await asyncio.sleep(self.sampling_rate)

    async def stop_experiment(self) -> bool:
        """
        Sends the equivalent stop command to each device putting the entire system at rest. TODO: Technically these
        can fail if communication has been severed, warn user of such later.
        """

        devices = [device for device in [self.bk_operator,
                                         self.temp_controller, self.pump_controller] if device is not None]

        await asyncio.gather(*[device.reset() for device in devices])

    async def _start_experiment(self):
        """
        Readies each device and sets the desired setpoint for each device using the values stored in the experiment.json file.
        """

        # note that the BK Power supply takes longer to ready and that the temp controller may be applying
        # temperature BEFORE the BK Power Supply is applying current.
        await asyncio.gather(self._ready_BK(),
                             self._ready_Pump_Controller(),
                             self._ready_Temp_Controller())

        with open(self.save_path, "w") as out:
            out.write("Current, Voltage, Temperature\n")

    async def _ready_BK(self) -> None:
        """
        Makes initial connection with the BK Power Supply, ensures that the Power Supply is correctly communicating
        with the software, sets the voltage limits of the power supply, then sets the current setpoint to the
        value given in the experiment.json file. The power supply immediately beings applying the current.
        """

        self.bk_operator = self._get_new_BK(self.bk_options)

        if(not await self.bk_operator.verify_connection()):
            raise ExperimentError("The BK Power Supply has failed to verify its connection")

        if (not await self.bk_operator.set_voltage_limits(self.bk_options["minimum-voltage"], self.bk_options["maximum-voltage"])):
            raise ExperimentError("The BK Power Supply has failed to set Experiment voltage limits.")

        if (not await self.bk_operator.set_current(self.bk_options["current-setpoint"])):
            raise ExperimentError("The BK Power Supply has failed to set the current setpoint")

    async def _ready_Pump_Controller(self) -> None:
        """
        Makes initial connection with the Pump Controller, ensures that the Pump Controller is correctly communicating
        with the software, and then turns on the Pump Controller.
        """

        self.pump_controller = self._get_new_PumpController(self.pump_options)

        if(not await self.pump_controller.verify_connection()):
            raise ExperimentError("The Pump Controller has failed to verify its connection.")

        if (not await self.pump_controller.turn_on()):
            raise ExperimentError("The Pump Controller has failed to turn on.")

    async def _ready_Temp_Controller(self) -> None:
        """
        Makes initial connection with the Temperature Controller, ensures that the Temperature Controller is correctly
        communicating with the software, and sets the temperature setpoint of the Temperature Controller to the value
        given in the experiment.json file.
        """

        self.temp_controller = self._get_new_TemperatureController(self.temperature_options)

        if(not await self.temp_controller.verify_connection()):
            raise ExperimentError("The Temperature Controller has failed to verify its connection")

        if(not await self.temp_controller.set_temperature(self.temperature_options["temperature-setpoint"])):
            raise ExperimentError("The Temperature Controller has failed to set the temperature setpoint.")

    async def _process_readings(self) -> bool:
        """
        Requests readings from all connected devices, validates these readings (and potentially raises an
        ExperimentError if readings are out of bounds), then saves to .csv file given in experiment.json file.
        """

        try:
            readings = await self._get_readings()
        except IOError as err:
            raise ExperimentError(f"Device communication error: {err}")

        self._throw_on_bad_readings(readings)

        with open(self.save_path, "a") as out:
            out.write(", ".join(map(str, readings)))
            out.write("\n")

    def _throw_on_bad_readings(self, readings: tuple) -> None:
        """
        Compares readings against known limits provided by the user and throws an ExperimentError if these
        limits are exceeded.
        """

        if(self.previous_voltage is not None and abs(self.bk_options["max-dV"]) < abs(readings[1] - self.previous_voltage)):
            raise ExperimentError(
                "The experiment stopped because the change in voltage exceeded the allowed tolerance for dV.")
        if(abs(readings[1]) > abs(self.bk_options["maximum-voltage"])):
            raise ExperimentError("The experiment stopped because the maximum voltage limit was reached.")

        if (abs(readings[1]) < abs(self.bk_options["minimum-voltage"])):
            raise ExperimentError("The experiment stopped because the minimum voltage limit was reached.")

        self.previous_voltage = readings[1]

    async def _get_readings(self) -> tuple:
        """
        Returns (current, voltage, temperature) from connected devices if available, does nothing with
        raised exceptions.
        """

        current = asyncio.create_task(self.bk_operator.get_current())
        voltage = asyncio.create_task(self.bk_operator.get_voltage())
        temperature = asyncio.create_task(self.bk_operator.get_voltage())
        await asyncio.gather(current, voltage, temperature)

        return (current.result(), voltage.result(), temperature.result())

    def _get_new_BK(self, bk_dict: dict) -> BKOperator:
        """
        Makes the initial serial connection with the BK Power Supply to the com port supplied in the
        experiment.json file. Pyserial will throw an IOError if the com port is not available to connect with.
        """

        try:
            return BKOperator(bk_dict["com-port"])
        except IOError:
            raise ExperimentError("Unable to establish communication with the BK power supply.")

    def _get_new_PumpController(self, pump_dict: dict) -> PumpController:
        """
        Makes the initial serial connection with the Pump Controller to the com port supplied in the
        experiment.json file. Pyserial will throw an IOError if the com port is not available to connect with.
        """

        try:
            return PumpController(pump_dict["com-port"])
        except IOError:
            raise ExperimentError("Unable to establish communication with the Pump Controller.")

    def _get_new_TemperatureController(self, temp_dict: dict) -> TemperatureController:
        """
        Makes the initial serial connection with the Temperature Controller to the com port supplied in the
        experiment.json file. Pyserial will throw an IOError if the com port is not available to connect with.
        """

        try:
            return TemperatureController(temp_dict["com-port"])
        except IOError:
            raise ExperimentError("Unable to establish communication with the Temperature Controller.")


class ExperimentError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message
