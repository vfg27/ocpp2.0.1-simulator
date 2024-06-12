from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI

class MyTopo(Topo):
    "Simple topology example."
    def build(self):
        "Create custom topo."
        # Add hosts and switches
        switch = self.addSwitch('s1')
        host1 = self.addHost('h1', ip='192.168.20.17/24')
        host2 = self.addHost('h2', ip='192.168.20.18/24')
        # Add links
        self.addLink(host1, switch)
        self.addLink(host2, switch)

if __name__ == '__main__':
    # Create the network
    topo = MyTopo()
    net = Mininet(topo)
    net.start()

    # Start the CLI
    CLI(net)

    # Stop the network
    net.stop()
