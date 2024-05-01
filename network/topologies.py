from ipmininet.iptopo import IPTopo


class CustomTopology(IPTopo):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)

    def build(self, *args, **kwargs):
        h1 = self.addHost("h1")
        h2 = self.addHost("h2")

        s1 = self.addSwitch("s1")
        s2 = self.addSwitch("s2")

        r1 = self.addRouter("r1")
        r2 = self.addRouter("r2")

        self.addLink(h1, s1, bw=1000)
        self.addLink(s1, r1, bw=1000, delay="1ms")

        self.addLink(r1, r2, bw=100, delay="15ms")

        self.addLink(r2, s2, bw=1000, delay="1ms")
        self.addLink(s2, h2, bw=1000)

        super().build(*args, **kwargs)
