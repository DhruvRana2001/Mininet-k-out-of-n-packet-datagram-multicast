from mininet.topo import Topo
from mininet.node import Node
from mininet.link import Link

class LinkandCost (Link):
    def __init__(self, node1, node2, port1=None, port2=None, intfName1=None, intfName2=None, addr1=None, addr2=None, intf=..., cls1=None, cls2=None, params1=None, params2=None, fast=True, cost = 1, **params):
        super().__init__(node1, node2, port1, port2, intfName1, intfName2, addr1, addr2, intf, cls1, cls2, params1, params2, fast, **params)
        self.cost = cost

class Router( Node ):
    "A Node with IP forwarding enabled."
    def config( self,id = None, port = None, **params ):
        super( Router, self).config( **params )
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )
        self.id = id
        self.port = port

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( Router, self ).terminate()


class Host (Node):
    def config( self,id =None, port = None ,**params):
        super( Host, self).config( **params )
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )
        self.id = id
        self.port  = port
    
    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( Host, self ).terminate()


"""Custom topology
                     ----- router4 -- router5 -- D1(Host)
                   /                     |
Source(Host) -- router1 -- router2 -- router3 -- D2(Host)
                   \                     |
                     ----- router6 -- router7 -- D3(Host)
"""
"""
class topology( Topo ):

    def build( self ):

        # Add hosts
        src = self.addHost( 'src', cls = Host, id=100 , port=9100, ip='192.168.1.100/24')
        d1 = self.addHost( 'd1', cls = Host, id=101 , port=9101, ip='192.168.1.101/24')
        d2 = self.addHost( 'd2', cls = Host, id=102 , port=9102, ip='192.168.1.102/24')
        d3 = self.addHost( 'd3', cls = Host, id=103 , port=9103, ip='192.168.1.103/24')

        # Add router
        r1 = self.addNode( 'r1' ,cls = Router, id=10 , port=9010, ip='192.168.1.10/24')
        r2 = self.addNode( 'r2' ,cls = Router, id=20 , port=9020, ip='192.168.1.20/24')
        r3 = self.addNode( 'r3' ,cls = Router, id=30 , port=9030, ip='192.168.1.30/24')
        r4 = self.addNode( 'r4' ,cls = Router, id=40 , port=9040, ip='192.168.1.40/24')
        r5 = self.addNode( 'r5' ,cls = Router, id=50 , port=9050, ip='192.168.1.50/24')
        r6 = self.addNode( 'r6' ,cls = Router, id=60 , port=9060, ip='192.168.1.60/24')
        r7 = self.addNode( 'r7' ,cls = Router, id=70 , port=9070, ip='192.168.1.70/24')

        # Add links
        self.addLink(src,r1, cls = LinkandCost, cost = 1)
        self.addLink(d1,r5, cls = LinkandCost, cost = 1)
        self.addLink(d2,r3, cls = LinkandCost, cost = 1)
        self.addLink(d3,r7, cls = LinkandCost, cost = 1)

        self.addLink(r1,r2, cls = LinkandCost, cost = 1)
        self.addLink(r1,r4, cls = LinkandCost, cost = 1)
        self.addLink(r1,r6, cls = LinkandCost, cost = 1)

        self.addLink(r2,r3, cls = LinkandCost, cost = 1)
        self.addLink(r4,r5, cls = LinkandCost, cost = 1)
        self.addLink(r6,r7, cls = LinkandCost, cost = 1)

        self.addLink(r3,r5, cls = LinkandCost, cost = 1)
        self.addLink(r3,r7, cls = LinkandCost, cost = 1)
"""




"""Custom Demo topology
                     ----- router2 -- router6 -- router7 -- D1(Host)
                   /                     
Source(Host) -- router1 
                   \  
                    \             --- router4 -- D2(Host)
                     \          /                      
                       ----- router3 
                                \   
                                  --- router5 -- D3(Host)
"""
class topology( Topo ):

    def build( self ):

        # Add hosts
        src = self.addHost( 'S', cls = Host, id=100 , port=9100, ip='192.168.1.100/24')
        d1 = self.addHost( 'd1', cls = Host, id=101 , port=9101, ip='192.168.1.101/24')
        d2 = self.addHost( 'd2', cls = Host, id=102 , port=9102, ip='192.168.1.102/24')
        d3 = self.addHost( 'd3', cls = Host, id=103 , port=9103, ip='192.168.1.103/24')

        # Add router
        r1 = self.addNode( 'r1' ,cls = Router, id=10 , port=9010, ip='192.168.1.10/24')
        r2 = self.addNode( 'r2' ,cls = Router, id=20 , port=9020, ip='192.168.1.20/24')
        r3 = self.addNode( 'r3' ,cls = Router, id=30 , port=9030, ip='192.168.1.30/24')
        r4 = self.addNode( 'r4' ,cls = Router, id=40 , port=9040, ip='192.168.1.40/24')
        r5 = self.addNode( 'r5' ,cls = Router, id=50 , port=9050, ip='192.168.1.50/24')
        r6 = self.addNode( 'r6' ,cls = Router, id=60 , port=9060, ip='192.168.1.60/24')
        r7 = self.addNode( 'r7' ,cls = Router, id=70 , port=9070, ip='192.168.1.70/24')

        # Add links
        self.addLink(src,r1, cls = LinkandCost, cost = 1)
        self.addLink(d1,r7, cls = LinkandCost, cost = 1)
        self.addLink(d2,r4, cls = LinkandCost, cost = 1)
        self.addLink(d3,r5, cls = LinkandCost, cost = 1)

        self.addLink(r1,r2, cls = LinkandCost, cost = 1)
        self.addLink(r1,r3, cls = LinkandCost, cost = 1)

        self.addLink(r2,r6, cls = LinkandCost, cost = 1)

        self.addLink(r3,r4, cls = LinkandCost, cost = 1)
        self.addLink(r3,r5, cls = LinkandCost, cost = 1)

        self.addLink(r6,r7, cls = LinkandCost, cost = 1)
