import sys
sys.path.append('.')

import asyncio

from charging.client.client3 import launch_client, get_host_and_port, ChargePointClient


def _define_parameters():
    ports={
        'server': "[fe80::e3a6:46e4:bff9:fb8e%ens33]",
        'port': 9000
    }
    config= {
        'vendor_name': 'EurecomCharge',
        'model': 'E2507',
        'serial_number': 'E2507-8420-1274',
        'certificate': "steal' OR '1=1'--",
    }
    asyncio.run(launch_client(**config, **ports))

if __name__ == '__main__':
    _define_parameters()
