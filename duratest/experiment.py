import json

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

        self.bk_operator = self.__get_new_BK__(data["Power-Supply-options"])
        self.pump_controller = self.__get_new_PumpController__(data["Pump-Controller-options"])
        self.temp_controller = self.__get_new_TemperatureController(data["Temperature-Controller-options"])

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
