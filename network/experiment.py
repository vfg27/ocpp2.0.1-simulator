from mininet.topo import Topo

class MyTopo( Topo ):
    "Simple topology example."

    def build( self ):
        "Create custom topo."

        # Add hosts and switches
        switch = self.addSwitch('s1')
        host1 = self.addHost('h1', ip='192.168.20.17/24')
        host2 = self.addHost('h2', ip='192.168.20.18/24')

        # Add links
        self.addLink(host1, switch)
        self.addLink(host2, switch)


topos = { 'mytopo': ( lambda: MyTopo() ) }