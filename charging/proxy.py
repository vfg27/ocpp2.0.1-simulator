from mitmproxy import http

# mitmproxy --listen-host 192.168.10.128 --listen-port 8080 --mode transparent


SERVER_IPV6_ADDRESS = "[fe80::e3a6:46e4:bff9:fb8e%ens33]"
SPECIFIC_PORT = 9000

def websocket_message(flow):
    if flow.websocket and flow.server_conn.ip_address.host == SERVER_IPV6_ADDRESS and flow.server_conn.address.port == SPECIFIC_PORT:
        print(flow.websocket.messages)

def start():
    print(f"Intercepting WebSocket traffic to and from {SERVER_IPV6_ADDRESS} on port {SPECIFIC_PORT}")

def response(flow):
    pass

def error(flow):
    pass