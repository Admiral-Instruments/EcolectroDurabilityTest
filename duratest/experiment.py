import json
import asyncio

from bk_operator import BKOperator
from pump_controller import PumpController
from temperature_controller import TemperatureController


class Experiment:
    def __init__(self):
        with open("experiment.json") as f:
            data = json.load(f)

        self.sampling_rate = data["sampling-rate"]
        self.duration = data["duration"]
        self.save_path = data["save-path"]

        self.bk_options = data["Power-Supply-options"]
        self.pump_options = data["Pump-Controller-options"]
        self.temperature_options = data["Temperature-Controller-options"]

        self.bk_operator = self.__get_new_BK__(self.bk_options)
        self.pump_controller = self.__get_new_PumpController__(self.pump_options)
        self.temp_controller = self.__get_new_TemperatureController(self.temperature_options)

    async def run_experiment(self):
        while self.duration > 0:
            self.__get_readings__()
            self.duration -= self.sampling_rate
            await asyncio.sleep(self.sampling_rate)

    def __get_readings__(self) -> bool:
        return True

    def __get_new_BK__(self, bk_dict: dict) -> BKOperator:
        try:
            ret = BKOperator(bk_dict["com-port"])

            return ret
        except IOError:
            print("Unable to establish communication with the BK power supply")

    def __get_new_PumpController__(self, pump_dict: dict) -> PumpController:
        try:

            ret = PumpController(pump_dict["com-port"])

            return ret
        except IOError:
            print("Unable to establish communication with the Pump Controller")

    def __get_new_TemperatureController(self, temp_dict: dict) -> TemperatureController:
        try:
            ret = TemperatureController(temp_dict["com-port"])

            return ret
        except IOError:
            print("Unable to establish communication with the Temperature Controller")
