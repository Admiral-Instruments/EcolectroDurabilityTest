# EcolectroDurabilityTest

## Use
This project is designed to use the [BK Precision 9115 Power
Supply](https://www.bkprecision.com/products/power-supplies/9115-1200w-multi-range-80v-60a-dc-power-supply.html), the
[Universal High Accuracy Digital Benchtop PID Controller with USB Temperature
Controller](https://www.omega.com/en-us/control-monitoring/controllers/pid-controllers/p/CS8DPT-Series) and the [Pump
Controller](https://www.admiralinstruments.com) to run a durability test on a system.

The user communicates with the program using the [experiment.json](duratest/experiment.json) file found in the source
(duratest) directory.

Inputs are as follows:
* **Power Supply**
    * COM Port (also known as serial communication port)
    * Applied Current (Units: Amperes)
    * Minimum Allowed Voltage (Units: Voltages)
    * Maximum Allowed Voltage (Units: Voltages)
    * Maximum change in Voltage between two readings, referred to has max-dV (Units: Voltages)
* **Temperature Control**
    * COM Port
    * Applied Temperature (Units: Celsius)
    * Maximum Temperature (Units: Celsius)
* **Pump Control**
    * COM Port
* **Other**
    * Sampling rate (each device will be polled together at this interval) (Units: Seconds)
    * Duration (Units: Seconds)
    * Save Path (the .csv file data will be kept in will be created from the given path)



## Structure and Data Flow

The program will read the parameters found in the json file and setup the initial connections with all devices at their
specified COM port. When all devices have successfully connected, the experiment will proceed at the given setpoint and
halt if any maximum or minimum end condition is hit. It is expected that every device will have a response acknowledging
that a request is successful. However, this might not be the case so we need to keep an eye out for that.

Data will be collected at intervals provided in the .json file for at least as long as the duration given in the .json
file. Because of the uncertainty in response times for some of these devices, the experiment may go on longer than
specified. This is because the application will wait until all devices have responded before proceeding to the next
waiting period between samples.

As of right now, debugging work needs to be done remotely by running the program with the BK power supply, temperature
controller and pump controller. The pump controller will require the user to run the application using Windows as we
will be calling an executable file to communicate with the pump controller.
