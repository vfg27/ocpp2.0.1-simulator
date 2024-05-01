import requests
import click


#g_host = '[::1]'
g_host = '[fe80::e3a6:46e4:bff9:fb8e%ens33]'
g_port = 8000
#g_host = '127.0.0.1'
#g_port = 8080


@click.group()
@click.option('--host', help='The host of the API server', default='[fe80::e3a6:46e4:bff9:fb8e%ens33]', type=str)
@click.option('--port', help='The port of the API server', default=8000, type=int)
def cli(host: str = '[fe80::e3a6:46e4:bff9:fb8e%ens33]', port: int = 8000):
    global g_host
    global g_port
    g_host = host
    g_port = port


@cli.command('login')
@click.option('--serial', help='The serial number of the CP', prompt='Serial number', required=True, type=str)
@click.option('--password', help='The password of the user', prompt='Password', required=True, type=str)
def _send_login_request(serial: str, password: str):
    send_login_request(serial, password, g_host, g_port)


def send_login_request(serial: str, password: str, host: str = '[fe80::e3a6:46e4:bff9:fb8e%ens33]', port: int = 8000):
    # Send request
    print(host)
    response = requests.get(f'http://{host}:{port}/api/login?serial={serial}&password={password}')

    # Check if the request was not successful (status code 200)
    if response.status_code == 403:
        click.echo(f"The charge point is already in the system. Do you want to change the password?")
        change = click.prompt('Yes/No')
        if change == 'Yes' or change == 'yes' or change == 'y':
            old_password = click.prompt('Old password')
            new_password = click.prompt('New password')
            response_change = requests.get(f'http://{host}:{port}/api/change_password?serial={serial}&old_password={old_password}&new_password={new_password}')
                # Check if the request was not successful (status code 200)
            if response_change.status_code != 200:
                click.echo(f"Error sending request: {response.status_code}")
        else:
             click.echo('Thank you. Goodbye!')
    if response_change.status_code != 200:
                click.echo(f"Error sending request: {response.status_code}")



@cli.command('reserve')
@click.option('--serial', help='The serial number of the charger', prompt='Serial number', required=True, type=str)
@click.option('--token-type', help='The type of the token', prompt='Token type', required=True, type=click.Choice(['Central', 'eMAID', 'ISO14443', 'ISO15693']))
@click.option('--token-id', help='The ID of the token', prompt='Token id', required=True, type=str)
def _send_reservation_request(serial: str, token_type: str, token_id: str):
    send_reservation_request(serial, token_type, token_id, g_host, g_port)


def send_reservation_request(serial: str, token_type: str, token_id: str, host: str = '[fe80::e3a6:46e4:bff9:fb8e%ens33]', port: int = 8080):
    # Send request
    response = requests.get(f'http://{host}:{port}/api/reserve_now/{serial}?type={token_type}&id_token={token_id}')

    # Check if the request was not successful (status code 200)
    if response.status_code != 200:
        click.echo(f"Error sending request: {response.status_code}")

@cli.command('list')
@click.option('--serial', help='The serial number of the charger', prompt='Serial number', required=True, type=str)
@click.option('--token-type', help='The type of the token', prompt='Token type', required=True, type=click.Choice(['Central', 'eMAID', 'ISO14443', 'ISO15693']))
@click.option('--token-id', help='The ID of the token', prompt='Token id', required=True, type=str)
def _list_events(serial: str, token_type: str, token_id: str):
    list_events(serial, token_type, token_id, g_host, g_port)


def list_events(serial: str, token_type: str, token_id: str, host: str = '[fe80::e3a6:46e4:bff9:fb8e%ens33]', port: int = 8080):
    # Send request
    response = requests.get(f'http://{host}:{port}/api/list/{serial}?type={token_type}&id_token={token_id}')

    # Check if the request was not successful (status code 200)
    if response.status_code != 200:
        click.echo(f"Error sending request: {response.status_code}")
    print(response.text)

if __name__ == '__main__':
    cli()
