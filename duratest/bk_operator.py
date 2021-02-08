class BKOperator:
    def __init__(self, com_port: str):
        """
        Attempts to make connection with a BK Operator 9115 power supply. If successful, the previous state
        of the power supply is not preserved, so this could interrupt an ongoing experiment. If connection
        was not successful, an IOError is thrown.
        """

        self.com_port = com_port

        successful = True

        if(not successful):
            raise IOError("Connection was not successful")

    def set_current(self, current: float) -> bool:
        """
        Instructs the BK power supply to set the current to the input argument, given in Amperes.
        """

        self.__send_command__("set current")

        # feed in command here for pyserial, then check the measured current for success
        return True

    def get_current(self) -> float:
        """
        Returns the current reading from the BK power supply in Amperes.
        """

        self.__send_command__("get current")

        return 4.2

    def get_voltage(self) -> float:
        """
        Returns the voltage reading from the BK power supply in Voltages.
        """

        self.__send_command__("get voltage")

        return 7.2

    def power_down(self) -> bool:
        """
        Powers down the BK power supply, returns true on success.
        """

        self.__send_command__("power down")

        return True

    def set_voltage_limits(self, min_voltage: float, max_voltage: float) -> bool:
        """
        Sets the voltage protection limits
        """

        self.__send_command__("set voltage limit")

    def __send_command__(self, command: str) -> bool:
        return True