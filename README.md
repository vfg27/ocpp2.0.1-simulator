# ocpp2.0.1-simulator
## Introduction
Welcome to the repository for the OCPP Protocol Simulator! The goal of this project is to provide an extensive and flexible Open Charge Point Protocol (OCPP) emulator. The OCPP standard protocol facilitates communication between central management systems (CSMs) and electric vehicle (EV) charging stations. With the increasing global usage of electric vehicles, there is a growing need for trustworthy testing and simulation tools. This implementation supports **OCPP 2.0.1** version. It has been tested on a Ubuntu 22.04.4 LTS VMware Virtual Machine with Python 3.10.12. 
## Features
* The emulation supports **OCPP Security Profile 1** and **OCPP Security Profile 1**. However, it can also be used without any Security Profile.
* The emulator supports three modes of operation (allow_multiple_serial_numbers): 0 (No) | 1 (Yes) | 2 (No, but allows to steal)
* It includes a script to generate custom (self-signed) certificates.
## Configuration and Installation
To get started with the OCPP Simulator, follow these steps:
1. **Clone the Repository**: Clone this repository to your local machine using the following command:
```
git clone https://github.com/vfg27/ocpp2.0.1-simulator
```
2. Install the virtual environment (it can also be used on a Windows system but you must execute the other install executable):
```
cd ocpp2.0.1-simulator/scripts/
bash install.sh
```
3. **Use the virtual environment installed and choose its python interpreter**
4. **Modify the server_config.yaml with the configuration that you prefer (inside the charging folder)**
5. **Execute the server.py and client.py scripts**: There are also some possible attacks scripts to this implementation in the scenarios folders. You have to execute them according to the security profile chosen.


We appreciate you choosing this OCPP Simulator to meet your needs for simulation and testing. Savor the smooth charging process! :)
