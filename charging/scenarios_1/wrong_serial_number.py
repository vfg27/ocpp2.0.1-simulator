import sys
sys.path.append('.')

import asyncio

from charging.client.client1 import launch_client, get_host_and_port, ChargePointClient


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
