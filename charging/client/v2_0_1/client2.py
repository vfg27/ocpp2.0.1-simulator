import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Optional, Callable, Awaitable, Dict, Any

import aioconsole
import ssl
from flask import cli
import websockets
from ocpp.routing import on, after
from ocpp.v201 import ChargePoint as Cp, call, call_result
#from ocpp.v16 import ChargePoint as Cp, call, call_result
from websockets import Subprotocol

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

logging.basicConfig(level=logging.ERROR)
sslkeylogfile = os.getenv('SSLKEYLOGFILE')
CA_BUNDLE_PATH =  os.path.join(os.getcwd(), 'cabundle.pem')
certificate_accepted = False
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.load_verify_locations(CA_BUNDLE_PATH)
context.check_hostname = False
context.keylog_filename = sslkeylogfile
#context.verify_mode = ssl.CERT_NONE



def _get_current_time() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S") + "Z"


class ChargePointClient(Cp):

    def __init__(self, id, connection, printed_name: Optional[str] = None):
        super().__init__(id, connection)
        if printed_name is not None:
            self.printed_name = printed_name
        else:
            self.printed_name = str(self.id)

    def print_message(self, message: str):
        print(f'[{self.printed_name}] {message}')

    @on("CertificateSigned")
    def on_certificate_signed(
        self,
        certificate_chain: str
    ):
        print(f"Got certificate")
        global certificate_accepted 
        try:
            valid = False

            # Convert the hex encoded string back to binary
            der_encoded = bytes.fromhex(certificate_chain)

            # Load the X.509 certificate from DER encoded binary
            certificate = x509.load_der_x509_certificate(der_encoded, default_backend()) 

            # Verify the certificate's signature
            public_key = certificate.public_key()
            try:
                public_key.verify(
                    certificate.signature,
                    certificate.tbs_certificate_bytes,
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
                print("Signature verification successful")
                valid = True
            except Exception as e:
                print("Signature verification failed:", e)
                valid = False
            if valid:
            # Check if the certificate has expired
                if certificate.not_valid_before_utc <= datetime.now(certificate.not_valid_before_utc.tzinfo) <= certificate.not_valid_after_utc:
                    print("Certificate is currently valid")
                    valid = True
                else:
                    print("Certificate has expired")
                    valid = False
            if valid:
                # Check certificate common name
                cn = None
                for attr in certificate.issuer:
                    if attr.oid == x509.NameOID.COMMON_NAME:
                        cn = attr.value
                        break
                if cn == 'eurecom.fr':
                    print("Certificate is from eurecom.fr")
                    valid = True
                else:
                    print("Certificate not valid")
                    valid = False
            certificate_accepted = valid
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            valid = False
            certificate_accepted = False

        if valid:
            status = "Accepted"
        else:
            status = "Rejected"
        return call_result.CertificateSignedPayload(
            status = status
        )


    async def send_heartbeat(
        self,
        interval: int = 10
    ):
        request = call.HeartbeatPayload()

        while True:
            # Send heartbeat
            await self.call(request)
            # Wait for interval
            await asyncio.sleep(interval)

    async def send_authorize(
        self,
        token: dict[str, str]
    ):
        return await self.call(call.AuthorizePayload(id_token=token))

    async def send_status_notification(
        self,
        connector_status: str,
        evse_id: int = 0,
        connector_id: int = 0
    ):
        return await self.call(call.StatusNotificationPayload(
            timestamp=_get_current_time(),
            connector_status=connector_status,
            evse_id=evse_id,
            connector_id=connector_id
        ))

    async def send_transaction_event_authorized(
        self,
        event_type: str,
        transaction_id: str,
        seq_no: int,
        id_token: dict[str, str]
    ):
        return await self.call(call.TransactionEventPayload(
            timestamp=_get_current_time(),
            event_type=event_type,
            seq_no=seq_no,
            transaction_info={'transactionId': transaction_id},

            trigger_reason='Authorized',
            id_token=id_token
        ))

    async def send_transaction_event_cable_plugged_in(
        self,
        event_type: str,
        transaction_id: str,
        seq_no: int
    ):
        return await self.call(call.TransactionEventPayload(
            timestamp=_get_current_time(),
            event_type=event_type,
            seq_no=seq_no,
            transaction_info={'transactionId': transaction_id},

            trigger_reason='CablePluggedIn'
        ))

    async def send_transaction_event_charging_state_changed(
        self,
        event_type: str,
        transaction_id: str,
        seq_no: int,
        charging_state: str
    ):
        return await self.call(call.TransactionEventPayload(
            timestamp=_get_current_time(),
            event_type=event_type,
            seq_no=seq_no,
            transaction_info={'transactionId': transaction_id, 'chargingState': charging_state},
            trigger_reason='ChargingStateChanged',
        ))

    async def send_certificate_request(self, ws):
        # Request Certificate
        requestCert = call.SignCertificatePayload(
            csr = "<certificate signing request>"
        )

        responseCert = await self.call(requestCert)
        if responseCert == 'Rejected':
            print("Certificate petition denied")
            return await ws.close()
        else: 
            print("Certificate petition accepted")
        

    async def send_boot_notification(
        self,
        serial_number: str,
        model: str,
        vendor_name: str,
        password: str,
        async_runnable: Optional[Callable[['ChargePointClient'], Awaitable[None]]] = None
    ):
        if certificate_accepted:
            # Send boot notification
            request = call.BootNotificationPayload(
                charging_station={"model": model, "vendor_name": vendor_name, "serial_number": serial_number},
                #charge_point_model= model,
                #charge_point_vendor= vendor_name,
                #charge_box_serial_number= serial_number,
                reason="PowerUp",
                custom_data={"vendorId": '', "password": password}
            )
            response = await self.call(request)

            # Check if boot notification is accepted
            if response.status != "Accepted":
                logging.error("Authorization failed")
                return

            # Schedule heartbeat to be run in background
            heartbeat_task = asyncio.create_task(self.send_heartbeat(response.interval))

            # Run "runnable" function (if available) to implement a specific scenario
            if async_runnable is not None:
                await async_runnable(self)
            else:
                self.print_message("Connected to server")

            # Await for heartbeat task to end (never)
            await heartbeat_task

    @on('ReserveNow')
    def on_reserve_now(
        self,
        id: int,
        expiry_date_time: str,
        id_token: Dict,
        connector_type: Optional[str] = None,
        evse_id: Optional[int] = None,
        group_id_token: Optional[Dict] = None,
        custom_data: Optional[Dict[str, Any]] = None,
    ):
        self.print_message(f'Got a new reservation request {id} from {id_token}')

        return call_result.ReserveNowPayload(
            status='Accepted'
        )


# Launches client and initializes server connection
async def launch_client(
    serial_number: str,
    model: str = 'Model',
    vendor_name: str = 'Vendor',
    server: str = "[::1]",
    port: int = 9000,
    password: str = '', 
    async_runnable: Optional[Callable[[ChargePointClient], Awaitable[None]]] = None,
    printed_name: Optional[str] = None
    ):
    # Open websocket
    async with websockets.connect(
            f"ws://{server}:9001/{serial_number}", subprotocols=[Subprotocol("ocpp2.0.1")]
            #f"ws://127.0.0.1:8080/steve/websocket/CentralSystemService/{serial_number}", subprotocols=[Subprotocol("ocpp1.6")]
    ) as ws:
        # Initialize CP
        cp = ChargePointClient(serial_number, ws, printed_name)

        # Start it
        try:
            await asyncio.gather(
                cp.start(),
                cp.send_certificate_request(ws)
            )
        except websockets.exceptions.ConnectionClosed:
            print(f"[{serial_number}] Connection was forcefully closed by the server")

    # Open websocket
    async with websockets.connect(
            f"wss://{server}:{port}/{serial_number}", subprotocols=[Subprotocol("ocpp2.0.1")]
            #proxy = "http://192.168.10.128:9000"
            #f"ws://127.0.0.1:8080/steve/websocket/CentralSystemService/{serial_number}", subprotocols=[Subprotocol("ocpp1.6")]
            , ssl=context
    ) as ws:
        # Initialize CP
        cp = ChargePointClient(serial_number, ws, printed_name)

        # Start it
        try:
            await asyncio.gather(
                cp.start(),
                cp.send_boot_notification(
                    serial_number,
                    model,
                    vendor_name,
                    password,
                    async_runnable
                )
            )
        except websockets.exceptions.ConnectionClosed:
            print(f"[{serial_number}] Connection was forcefully closed by the server")


def get_host_and_port() -> dict[str, str]:
    # Get host and port from command line, if not default values of main function will be used
    arg_names = ['server', 'port']
    return dict(zip(arg_names, sys.argv[1:]))


# Prints the given message and awaits for a button press, in an asynchronous way
async def wait_for_button_press(message: str):
    await aioconsole.ainput(f'\n{message} | Press any key to continue...\n')

def _define_parameters():
    ports={
        'server': "[fe80::e3a6:46e4:bff9:fb8e%ens33]",
        'port': 9000
    }
    config= {
        'vendor_name': 'EurecomCharge',
        'model': 'E2507',
        'serial_number': 'E2507-8420-1274',
        'password': 'HPEufO4u3IMl1G'
    }
    asyncio.run(launch_client(**config, **ports))
if __name__ == '__main__':
    _define_parameters()
