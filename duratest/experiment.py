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
        self.__start_experiment__()
        while self.duration > 0:
            self.__save_reading__()
            self.duration -= self.sampling_rate
            await asyncio.sleep(self.sampling_rate)

    def __start_experiment__(self):
        self.bk_operator.set_current(self.bk_options["current-setpoint"])
        self.temp_controller.set_temperature(self.temperature_options["temperature-setpoint"])
        with open(self.save_path, "w") as out:
            out.write("Current, Voltage, Temperature\n")

    def __save_reading__(self) -> bool:
        with open(self.save_path, "a") as out:
            readings = map(str, self.__get_readings__())
            out.write(", ".join(readings))
            out.write("\n")

    def __get_readings__(self) -> tuple:
        return (1, 2, 3)

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
