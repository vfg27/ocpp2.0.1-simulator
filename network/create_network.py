from ipmininet.cli import IPCLI
from ipmininet.ipnet import IPNet
from mininet.log import lg

from topologies import CustomTopology


TERMINAL_SPAWN = {
    'h1': 1,
    'h2': 2
}

lg.setLogLevel('info')

net = IPNet(topo=CustomTopology(), use_v4=False, use_v6=True)

try:
    net.start()

    for h in net.hosts:
        if h.name in TERMINAL_SPAWN:
            for i in range(TERMINAL_SPAWN[h.name]):
                h.cmdPrint(f'/usr/bin/dbus-launch ./scripts/new_terminal.sh {h.name} &')

    IPCLI(net)

finally:
    net.stop()
