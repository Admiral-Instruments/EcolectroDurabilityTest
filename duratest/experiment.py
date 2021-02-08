import json

from bk_operator import BKOperator


class Experiment:
    def __init__(self):
        with open("experiment.json") as f:
            data = json.load(f)

        self.sampling_rate = data["sampling-rate"]
        self.duration = data["duration"]
        self.save_path = data["save-path"]

        self.bk_operator = self.__get_new_BK__(data["Power-Supply-options"])

    def __get_new_BK__(self, bk_dict: dict) -> BKOperator:
        ret = BKOperator(bk_dict["com-port"])

        return ret
