import Topo
from Network import network
from mininet.net import Mininet

Nodes = [{"name":"S", "id":100, "ip":"192.168.1.100", "port":9100, "neigbours":["r1"], "costs":[1]},
         {"name":"d1", "id":101, "ip":"192.168.1.101", "port":9101, "neigbours":["r7"], "costs":[1]},
         {"name":"d2", "id":102, "ip":"192.168.1.102", "port":9102, "neigbours":["r4"], "costs":[1]},
         {"name":"d3", "id":103, "ip":"192.168.1.103", "port":9103, "neigbours":["r5"], "costs":[1]},
         {"name":"r1", "id":10, "ip":"192.168.1.10", "port":9010, "neigbours":["S","r2","r3"], "costs":[1,1,1]},
         {"name":"r2", "id":20, "ip":"192.168.1.20", "port":9020, "neigbours":["r1","r6"], "costs":[1,1]},
         {"name":"r3", "id":30, "ip":"192.168.1.30", "port":9030, "neigbours":["r1","r4","r5"], "costs":[1,1,1]},
         {"name":"r4", "id":40, "ip":"192.168.1.40", "port":9040, "neigbours":["r3","d2"], "costs":[1,1]},
         {"name":"r5", "id":50, "ip":"192.168.1.50", "port":9050, "neigbours":["r3","d3"], "costs":[1,1]},
         {"name":"r6", "id":60, "ip":"192.168.1.60", "port":9060, "neigbours":["r2","r7"], "costs":[1,1]},
         {"name":"r7", "id":70, "ip":"192.168.1.70", "port":9070, "neigbours":["r6","d1"], "costs":[1,1]}]


topo = Topo.topology( )
#net = Mininet(topo,controller=None)

# 1. Build Using Dict
# network.intialize_network_from_list(Nodes)
# 2. Build Using Topology (Prefered) (Requires the use of made custom cls in Topo file)
network.intialize_network_from_topology(topo)
# 3. Build Using Net (Requires the use of made custom cls in Topo file) (Uses More resrources)
# network.intialize_network_from_net(net)


# For testing purpose to visualise graph
"""
for v in network:
    print ('\nNetwork.nodes_dict[%s]: \n%s' %(v.get_name(), network.nodes_dict[v.get_name()]))
"""