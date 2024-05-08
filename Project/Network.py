from NetworkNode import Node

from mininet.net import Mininet
from mininet.topo import Topo

import sys
import heapq
import itertools

class Network:
    def __init__(self):
        self.nodes_dict = {}
        self.num_nodes = 0

    def __iter__(self):
        return iter(self.nodes_dict.values())
    
    def add_node(self, node:dict):
        self.num_nodes = self.num_nodes + 1
        new_vertex = Node(node)
        self.nodes_dict[node["name"]] = new_vertex
        return new_vertex
    
    def get_node_by_name(self, node):

        if type(node) == dict:
            node = node["name"]

        if type(node) == Node:
            node = node.get_name()

        if node in self.nodes_dict:
            return self.nodes_dict[node]
        else:
            return None
    
    def get_node_by_id(self, id):

        node = None
        for nodes in self:
            if nodes.get_id() == id:
                return nodes
        return node
    
    def get_all_node(self):
        return self.nodes_dict
    
    def add_link(self, frm, to, cost = 1):
        if type(frm) == dict:
            frm = frm["name"]

        if type(to) == dict:
            to = to["name"]

        if frm not in self.nodes_dict:
            print(f"Node {frm} does not exist in the network. Please Ensure that it is created before creating a link")
            return
        
        if to not in self.nodes_dict:
            print(f"Node {to} does not exist in the network. Please Ensure that it is created before creating a link")
            return
        
        if to not in self.nodes_dict[frm].get_neighbours():
            self.nodes_dict[frm].add_neighbor(self.nodes_dict[to], cost)
        
        if frm not in self.nodes_dict[to].get_neighbours():
            self.nodes_dict[to].add_neighbor(self.nodes_dict[frm], cost)
    
    """
    A method to initialize a network from list of nodes
    """
    def intialize_network_from_list(self,nodes:list):
        #1. Add all nodes from the list
        for node in nodes:
            self.add_node(node)
        
        #2. Add links between nodes
        for node in nodes:
            for neigbour,cost in zip(node["neigbours"],node["costs"]):
                self.add_link(node,neigbour,cost)
        
        #3. Create routing table for each node
        self.create_routingTables()
    
    """
    A method to initialize a network from Mininet net that uses custom cls
    """
    def intialize_network_from_net(self,net:Mininet):
        #1. Add all nodes from the list
        for node_name in net.keys():
            net_node = net[node_name]
            node = {"name":net_node.name,"ip":net_node.IP(),"id":net_node.id,"port":net_node.port}
            self.add_node(node)
        
        #2. Add links between nodes
        for link in net.links:
            self.add_link(link.intf1.node.name,link.intf2.node.name,link.cost)

        #3. Create routing table for each node
        self.create_routingTables()
    
    """
    A method to initialize a network from Mininet topology that uses custom cls
    """
    def intialize_network_from_topology(self,topo:Topo):
        #1. Add all nodes from the list
        for node_name in topo.nodes():
            node_info = topo.nodeInfo(node_name)
            node = {"name":node_name,"ip":node_info["ip"].split("/")[0],"id":node_info["id"],"port":node_info["port"]}
            self.add_node(node)
        
        #2. Add links between nodes
        for link in topo.links():
            link_info = topo.linkInfo(link[0],link[1])
            self.add_link(link_info["node1"],link_info["node2"],link_info["cost"])

        #3. Create routing table for each node
        self.create_routingTables()

    def set_all_nodes_to_default (self):
        for nodes in self:
            nodes.set_visited(False)
            nodes.set_previous(None)
            nodes.set_distance(sys.maxsize)
    
    def create_routingTables(self):   
        for from_node in self:
            self.set_all_nodes_to_default()
            self.dijkstra(from_node)
            for to_node in self:   
                if to_node == from_node:
                    continue
                
                path = self.shortest_path(to_node)
                try:
                    if (path[0][1] == from_node.get_id() and path[0][0] == 0): 
                        from_node.routingTable[to_node.get_id()] = path
                except:
                    print(f"{to_node.get_id()} is not reachable from {from_node.get_id()}")           
    
    def shortest_path(self,target):
        path = []
        path.append((target.get_distance(),target.get_id()))

        while target.get_previous():  
            target = target.get_previous()
            path.append((target.get_distance(),target.get_id()))

        path.reverse()
        return path

    def dijkstra(self, start):
        # Set the distance for the start node to zero 
        start.set_distance(0)

        # Put tuple pair into the priority queue
        unvisited_queue = [(node.get_distance(),node.get_id(),node) for node in self]
        heapq.heapify(unvisited_queue)

        while len(unvisited_queue):
            # Pop a node with the smallest distance 
            closet_node = heapq.heappop(unvisited_queue)
            current = closet_node[2]
            current.set_visited(True)

            for next in current.get_neighbours():
                # if visited, skip
                if next.visited:
                    continue
                new_dist = current.get_distance() + current.get_cost(next)
                
                if new_dist < next.get_distance():
                    next.set_distance(new_dist)
                    next.set_previous(current)

            # Rebuild heap
            # 1. Pop every item
            while len(unvisited_queue):
                heapq.heappop(unvisited_queue)
            # 2. Put all vertices not visited into the queue
            unvisited_queue = [(node.get_distance(),node.get_id(),node) for node in self if not node.visited]
            heapq.heapify(unvisited_queue)
    
    def get_dynamic_RP_id(self,src, destinations, k,option = -1):
       
        if k > len(destinations):
            print(f"\nValue of K ({k}) is greater than number of destinations ({len(destinations)})\n")
            return

        # Two (2) Options 
        # 1. Run Dijkstra for each router and check the distance on each destiantion and get router with min avg distance
        # 2. Since we already build routing table using Dijkstra on each node for the network we can just check the table of each router and pick the one that lead to min min avg distance 
        
        if option < 0 or option > 2:
            print("\nTwo (2) options to find Dynamic RP :-")
            print("    1. Use Dijkstra On Each Router")
            print("    2. Use Routing Table Of Each Router")

            while option < 0  or option > 2:
                option = int(input("Choose an option : "))
                if option < 0  or option > 2:
                    print("\n Incorrect Option. Please Try Again !!!\n")
            print()

        destinations = sorted(destinations)
        dynamic_rp_id = None
        min_distance = sys.maxsize
        min_distance_dst_comb = None
        dst_comb = sorted(list(itertools.combinations(destinations,k))) # k choose n combination(s) of destination

        # Option 1. Run Dijkstra
        if option == 1:      
            # Run Dijkstra on all nodes excpet the ones in destinations or src
            for node in self:
                self.set_all_nodes_to_default()
                if node.get_id() in destinations or node.get_id() in [src]:
                    continue
                self.dijkstra(node)
                # Get the disatnces from the destinations nodes
                for dst in dst_comb:
                    distances = [self.get_node_by_id(x).get_distance() for x in dst]
                    # Find combiantion of k destinaitons that lead to smallest avg_dist
                    avg_distance = sum(distances)/len(distances)  
                    # Save the k destination and cost as min
                    if avg_distance < min_distance:
                        min_distance = avg_distance
                        min_distance_dst_comb = list(dst)
                        dynamic_rp_id = node.get_id()
        
        # Option 2. Read Routing Table
        elif option == 2: 
            for node in self:
                if node.get_id() in destinations or node.get_id() in [src]:
                    continue               
                for dst in dst_comb:
                    # Find the routes to destination and thier distance          
                    distances = [node.get_routingTable()[x][-1][0] for x in dst]
                    avg_distance = sum(distances)/len(distances)
                    # save the k destination and cost as min
                    if avg_distance < min_distance:
                        min_distance = avg_distance
                        min_distance_dst_comb = list(dst)
                        dynamic_rp_id = node.get_id()
                    
        return dynamic_rp_id,min_distance_dst_comb,min_distance

network = Network()
