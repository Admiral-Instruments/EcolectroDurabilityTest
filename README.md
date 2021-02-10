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
* **Pump Control**
    * COM Port
* **Other**
    * Sampling rate (each device will be polled together at this interval) (Units: Seconds)
    * Duration (Units: Seconds)
    * Save Path (the .csv file data will be kept in will be created from the given path)



## Structure and Data Flow