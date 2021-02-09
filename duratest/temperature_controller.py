class TemperatureController:

    def __init__(self, com_port: str):
        self.com_port = com_port

    def set_temperature(self, temperature: float) -> bool:
        self.__send_command(f"{temperature} set")

    def __send_command(self, command: str):
        # send command through serial port
        test = 0
