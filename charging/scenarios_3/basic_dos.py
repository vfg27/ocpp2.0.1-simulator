import sys
sys.path.append('.')

import asyncio
import random
import time

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
    from charging.client.v2_0_1.client3 import launch_client, get_host_and_port, ChargePointClient
elif VERSION == 'v1_6':
    from charging.client.v1_6.client3 import launch_client, get_host_and_port, ChargePointClient

N_INSTANCES = 10_000

def _get_random_config() -> dict[str, str]:
    return {
        'vendor_name': 'EurecomCharge',
        'model': 'E2507',
        'serial_number': f'E2507-{random.randint(0, 9999):04}-{random.randint(0, 9999):04}',
        'password': 'HPEufO4u3IMl1G',
        'server': "[fe80::e3a6:46e4:bff9:fb8e%ens33]",
        'port': 9000
    }


async def _no_action(_: ChargePointClient):
    pass


async def main():
    tasks = []

    print(f"Launching {N_INSTANCES} clients...")

    start = time.time()

    for i in range(N_INSTANCES):
        # Launch client
        tasks.append(asyncio.create_task(launch_client(**_get_random_config(), **get_host_and_port(), async_runnable=_no_action)))
        # Sleep for some time to distribute clients over 10 seconds
        await asyncio.sleep(10/N_INSTANCES)

    print(f"All clients launched in {time.time() - start} seconds")

    # Await all clients
    for i in range(N_INSTANCES):
        await tasks[i]


if __name__ == "__main__":
    asyncio.run(main())
