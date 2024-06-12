# ocpp2.0.1-simulator
## Introduction
Welcome to the repository for the OCPP Simulator! The goal of this project is to provide an extensive and flexible Open Charge Point Protocol (OCPP) emulator. The OCPP standard protocol facilitates communication between central management systems (CSMs) and electric vehicle (EV) charging stations. With the increasing global usage of electric vehicles, there is a growing need for trustworthy testing and simulation tools. This implementation supports **OCPP 2.0.1** version. It has been tested on a Ubuntu 22.04.4 LTS VMware Virtual Machine with Python 3.10.12. 
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

## Mininet

The simulator can run on **Mininet** or **IPMininet**. I have created a simple topology to test the simulation but it works also on more complicated topologies. For it to work you have to:
1. Install Mininet/IPmininet:
```
pip install mininet
pip install ipmininet
```
2. Run the topology with one the following command
```
python3 mininet/simple_topology.py
python3 ipmininet/simple_topology.py
```

3. Launch the server in one host with this commands (you should modify the code to add the IP address of the host):
   * From the Mininet/IPMininet terminal:
    ```
    xterm h1
    ```
   * From the opened host terminal:
    ```
    source venv/bin/activate
    python3 charging/server.py
    ```
4. Launch the client in one host with this  command (you should modify the code to add the IP address where the server is listening):
   * From the Mininet/IPMininet terminal:
    ```
    xterm h2
    ```
   * From the opened host terminal:
    ```
    source venv/bin/activate
    python3 charging/client.py
    ```

Other implementation done is the possibility of having multiple hosts in a Mininet/IPMininet Virtual Machine and the server running in another Virtual Machine (I tried this on **VMWare**).  In order to make It work you should do:

1. Install Mininet/IPmininet in the first machine:
```
pip install mininet
pip install ipmininet
```
2. Run the topology with one the following command
```
python3 mininet/simple_topology.py
python3 ipmininet/simple_topology.py
```

3. Launch the server in the second Virtual Machine. You can do it as before or, if you want to do it from a terminal, you can do:
```
source venv/bin/activate
python3 charging/server.py
```
4. Launch the client in the hosts with this  command (you should modify the code to add the IP address where the server is listening):
   * From the Mininet/IPMininet terminal:
    ```
    xterm h1
    ...
    ```
   * From the opened hosts terminals:
    ```
    source venv/bin/activate
    python3 charging/client.py
    ```
5. Configure Mininet. From its terminal you should run:
```
source routes.mn
```

It is important to notice that this last feature only works with **IPv4** addresses, so, you should modify the code so make the server listen to a IPv4 address.

We appreciate you choosing this OCPP Simulator to meet your needs for simulation and testing. Savor the smooth charging process! :)
