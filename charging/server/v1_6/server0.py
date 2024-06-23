import sys
sys.path.append('.')

import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

import websockets
import yaml
from ocpp.routing import on, after
from ocpp.v16 import ChargePoint as Cp, call, call_result, datatypes, enums
from websockets import Subprotocol

from charging.db import get_event, purge_events

logging.basicConfig(level=logging.INFO)


SERVER_CONFIG_FILE = 'charging/server_config.yaml'

# Will be loaded from server_config.yaml on startup
ACCEPTED_TOKENS = []
ACCEPTED_CHARGES = []
ALLOW_MULTIPLE_SERIAL_NUMBERS = 0
MAX_CONNECTED_CLIENTS = 100_000
HEARTBEAT_INTERVAL = 10

# Holds ID and instance of all connected clients
connected_clients = []
duplicated_clients = {}


def _get_current_time() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S") + "Z"


def _get_personal_message(message: str) -> dict:
    return {
        'format': 'ASCII',
        'language': 'en',
        'content': message
    }


# Check if user can be authorized
def _check_authorized(id_token: Dict) -> str:
    # Check if type is correct
    if id_token['type'] not in ('Central', 'eMAID', 'ISO14443', 'ISO15693'):
        return 'Unknown'

    # Check if token is hexadecimal
    try:
        # Check if it can be converted to int from base 16
        int(id_token['id_token'], 16)
    except ValueError:
        return 'Unknown'

    # Check if it respects the specs of the type
    if id_token['type'] == 'Central':
        # Everything is accepted
        pass

    elif id_token['type'] == 'eMAID':
        # Not allowed in this implementation
        return 'Invalid'

    elif id_token['type'] == 'ISO14443':
        # Check if length is either 4 or 7 bytes
        if len(id_token['id_token']) != 8 and len(id_token['id_token']) != 14:
            return 'Invalid'

    elif id_token['type'] == 'ISO15693':
        # Check if length is 8 bytes
        if len(id_token['id_token']) != 16:
            return 'Invalid'

    else:
        return 'Unknown'

    # Check if token is in allowed list
    for i in ACCEPTED_TOKENS:
        if i['type'] == id_token['type'] and i['id_token'] == id_token['id_token']:
            return 'Accepted'

    # If no matching token was found in list
    return 'Invalid'


# Check if new CP is authorized based on vendor, model and serial number
def _check_charger(vendor_name: str, model: str, serial_number: str) -> bool:
    for i in ACCEPTED_CHARGES:
        # Check if vendor_name and model match
        if i['vendor_name'] == vendor_name and i['model'] == model:
            # Check if regex matches
            if re.match(i['serial_number_regex'], serial_number):
                return True

    # If no model match, return False
    return False


class ChargePointServer(Cp):

    is_booted: bool = False
    is_authorized: bool = False
    status: str = 'Available'
    charging_state: str = 'Idle'

    last_reservation_id = 0
    transaction_counter = 0

    # Periodically check for new connection
    async def _check_connections(self, interval: int = 0.0001, id: str = '', ws : websockets = None):
        await asyncio.sleep(1)
        while True:
            if duplicated_clients.get(id)==1:
                del duplicated_clients[id]
                return await ws.close()
            # Wait for set time
            await asyncio.sleep(interval)

    # Periodically check for new reservation requests
    async def _check_reservations(self, interval: int = 1):
        while True:
            # Get first reserve_now event
            data = get_event('reserve_now', target=self.id, first_acceptable_id=self.last_reservation_id + 1)

            # If event is there
            if data is not None:
                logging.info(f"Processing event reserve_now with data {data}")

                event_id, token = data

                # Send ReserveNow payload
                await self.send_reserve_now(
                    id=event_id,
                    expiry_date_time=(datetime.utcnow() + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S") + "Z",
                    id_token=token["id_token"]
                )

                # Set new last reservation id to current id
                self.last_reservation_id = event_id

            # Wait for set time
            await asyncio.sleep(interval)

    @on("BootNotification")
    async def on_boot_notification(
        self,
        charge_point_model= str,
        charge_point_vendor= str,
        charge_box_serial_number= str
    ):
        logging.info(f"Got boot notification from {charge_box_serial_number}")
    
        # Check if new CP has valid vendor, model and serial number
        self.is_booted = _check_charger(model=charge_point_model, vendor_name=charge_point_vendor, serial_number=charge_box_serial_number)

        if self.is_booted:
            if charge_box_serial_number in duplicated_clients:
                duplicated_clients[charge_box_serial_number] = 1
        else:
            if charge_box_serial_number in duplicated_clients:
                del duplicated_clients[charge_box_serial_number]

        return call_result.BootNotificationPayload(
            current_time=_get_current_time(),
            interval=HEARTBEAT_INTERVAL,
            status=('Accepted' if self.is_booted else 'Rejected')
        )

    @after("BootNotification")
    async def after_boot_notification(self, *args, **kwargs):
        # If the CP was not booted (which means rejected)
        if not self.is_booted:
            # Force close websocket
            await self._connection.close()

    @on("Heartbeat")
    def on_heartbeat(
        self,
        custom_data: Optional[Dict[str, Any]] = None
    ):
        return call_result.HeartbeatPayload(
            current_time=_get_current_time()
        )

    @on("Authorize")
    def on_authorize(
        self,
        id_token: Dict,
        certificate: Optional[str] = None,
        iso15118_certificate_hash_data: Optional[List] = None,
        custom_data: Optional[Dict[str, Any]] = None
    ):
        logging.info(f"Got authorization request from {id_token}")

        return call_result.AuthorizePayload(id_tag_info=datatypes.IdTagInfo(status=_check_authorized(id_token)))

    @on("StatusNotification")
    def on_status_notification(
        self,
        timestamp: str,
        connector_status: str,
        evse_id: int,
        connector_id: int,
        custom_data: Optional[Dict[str, Any]] = None
    ):
        self.status = connector_status

        return call_result.StatusNotificationPayload()


    @on("AuthorizePayload")
    def on_authorize(self, id_tag: str):
        logging.info(f"Authorizing ID tag {id_tag}")

        # Check if authorized
        auth_result = _check_authorized({"idToken": id_tag})
        if auth_result != "Accepted":
            logging.error(f"User is not authorized for reason {auth_result}")
            return call_result.AuthorizePayload(id_tag_info=datatypes.IdTagInfo(status=_check_authorized(auth_result)))

        logging.info(f"User is authorized")
        self.is_authorized = True
        return call_result.AuthorizePayload(id_tag_info=datatypes.IdTagInfo(status="Accepted"))

    @on("StartTransactionPayload")
    def on_start_transaction(self, id_tag: str, meter_start: int, timestamp: str):
        logging.info(f"Starting transaction for ID tag {id_tag}")

        if not self.is_authorized:
            logging.error("User is not authorized to start transaction")
            return

        transaction_counter += 1
        current_time = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        transaction_id = f"{current_time}{self.transaction_counter:04}"
        transaction_id = int(transaction_id)

        self.current_transaction_id = transaction_id

        return call_result.StartTransactionPayload(
            transaction_id=transaction_id,
            id_tag_info=datatypes.IdTagInfo(status="Accepted")
        )

    @on("StopTransactionPayload")
    def on_stop_transaction(self, transaction_id: int, meter_stop: int, timestamp: str):
        logging.info(f"Stopping transaction with ID {transaction_id}")
        return call_result.StopTransactionPayload(
           id_tag_info=datatypes.IdTagInfo(status="Accepted")
        )

    async def send_reserve_now(
        self,
        id: int,
        expiry_date_time: str,
        id_token: str,
        connector_type: Optional[str] = None,
        evse_id: Optional[int] = None,
        group_id_token: Optional[Dict] = None,
        custom_data: Optional[Dict[str, Any]] = None
    ):
        await self.call(call.ReserveNowPayload( 
            connector_id=1,
            expiry_date=expiry_date_time,
            id_tag=id_token,
            reservation_id=id
        ))


async def on_connect(websocket, path):
    # Check if protocol is specified
    try:
        requested_protocols = websocket.request_headers["Sec-WebSocket-Protocol"]
    except KeyError:
        logging.error("Client hasn't requested any protocol. Closing Connection")
        return await websocket.close()

    # Check if protocol matches with the one on the server
    if websocket.subprotocol:
        logging.info("Protocols Matched: %s", websocket.subprotocol)
    else:
        logging.error(f"Protocols Mismatched: client is using {websocket.subprotocol}. Closing connection")
        return await websocket.close()

    # Get id from path
    charge_point_id = path.strip("/")
    
    # Initialize CP
    cp = ChargePointServer(charge_point_id, websocket)

    # If only one CP per id is allowed, check it doesn't exist
    if ALLOW_MULTIPLE_SERIAL_NUMBERS == 0:
        for cp_id, cp in connected_clients:
            if cp_id == charge_point_id:
                logging.error(f"Client tried to connect with ID {cp_id}, but another client already exists")
                return await websocket.close()

    # Add to list of connected clients
    if connected_clients != []:
        for item in connected_clients:
            if item[0] == charge_point_id:
                logging.info(f"Client duplicated detected with id: {charge_point_id}")
                duplicated_clients[charge_point_id] = 0
            if ALLOW_MULTIPLE_SERIAL_NUMBERS == 2:
                connected_clients.remove(item)
    #await asyncio.sleep(3)

    connected_clients.append((charge_point_id, cp))

    if len(connected_clients) >= MAX_CONNECTED_CLIENTS:
        logging.error("Server is overloaded, quitting")
        quit(2)

    # Start and await for disconnection
    try:
        if ALLOW_MULTIPLE_SERIAL_NUMBERS == 1 or ALLOW_MULTIPLE_SERIAL_NUMBERS == 0:
            await asyncio.gather(cp.start(), cp._check_reservations())
        elif ALLOW_MULTIPLE_SERIAL_NUMBERS == 2:
            await asyncio.gather(cp.start(), cp._check_reservations(), cp._check_connections(id=charge_point_id, ws = websocket))
    except websockets.exceptions.ConnectionClosed:
        logging.info(f"Client {charge_point_id} disconnected")
        if (charge_point_id, cp) in connected_clients:
            # Remove from list of connected clients
            connected_clients.remove((charge_point_id, cp))


def load_config() -> bool:
    global ACCEPTED_TOKENS
    global ACCEPTED_CHARGES
    global ALLOW_MULTIPLE_SERIAL_NUMBERS
    global MAX_CONNECTED_CLIENTS
    global HEARTBEAT_INTERVAL

    # Open server config file
    with open(SERVER_CONFIG_FILE, "r") as file:
        try:
            # Parse YAML content
            content = yaml.safe_load(file)

            # Set accepted tokens
            if "accepted_tokens" in content:
                ACCEPTED_TOKENS = content["accepted_tokens"]

            # Set accepted chargers
            if "accepted_chargers" in content:
                ACCEPTED_CHARGES = content["accepted_chargers"]

            # Set security parameters
            if "security" in content:
                if "allow_multiple_serial_numbers" in content["security"]:
                    ALLOW_MULTIPLE_SERIAL_NUMBERS = content["security"]["allow_multiple_serial_numbers"]

                if "max_connected_clients" in content["security"]:
                    MAX_CONNECTED_CLIENTS = content["security"]["max_connected_clients"]

                if "heartbeat_interval" in content["security"]:
                    HEARTBEAT_INTERVAL = content["security"]["heartbeat_interval"]

        except yaml.YAMLError as e:
            print('Failed to parse server_config.yaml')
            return False

        return True


async def main():
    # Load config file
    if not load_config():
        quit(1)

    # Purge DB
    purge_events()

    # Start websocket with callback function
    server = await websockets.serve(
        #on_connect, "::", 9000, subprotocols=[Subprotocol("ocpp2.0.1")]
        on_connect, "fe80::e3a6:46e4:bff9:fb8e%ens33", 9000, subprotocols=[Subprotocol("ocpp1.6")]
    )

    # Wait for server to be closed down
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
