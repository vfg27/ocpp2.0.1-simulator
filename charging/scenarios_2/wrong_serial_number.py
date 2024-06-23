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
    from charging.client.v2_0_1.client2 import launch_client, get_host_and_port, ChargePointClient
elif VERSION == 'v1_6':
    from charging.client.v1_6.client2 import launch_client, get_host_and_port, ChargePointClient


async def main():
    config = {
        'vendor_name': 'EurecomCharge',
        'model': 'E2507',
        'serial_number': 'E2507-abcd-efgh',  # Wrong serial number
        'password': 'abcd',
        'server': "[fe80::e3a6:46e4:bff9:fb8e%ens33]",
        'port': 9000
    }

    await launch_client(**config, **get_host_and_port())


if __name__ == "__main__":
    asyncio.run(main())
