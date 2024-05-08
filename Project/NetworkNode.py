import sys

"""
A Node has all information about itself and holds the neighbours info
"""
class Node:
    def __init__(self,node:dict):
        self.id = node["id"]
        self.name = node["name"]
        self.ip = node["ip"]
        self.port = node["port"]
        self.neighbours = {}


        self.routingTable = {}
        # Set distance to infinity for all nodes
        self.distance = sys.maxsize
        # Mark all nodes unvisited        
        self.visited = False  
        # Predecessor
        self.previous = None
    
    def __str__(self):
        string = f"{self.name} :-" 
        string = string + f"\n    ID : {self.id}  IP : {self.ip}  port : {self.port}"
        string = string + f"\n    neighbours : {[node.id for node in self.neighbours]}"
        string = string + f"\n    Costs : {list(self.neighbours.values())}"
        string = string + f"\n    Routing Table :-"
        for route in self.routingTable:
            string = string + f"\n        {route} : {self.routingTable[route]}"
        return string

    def add_neighbor(self, neighbor, cost=1):
        self.neighbours[neighbor] = cost
    
    def get_connections(self):
        return self.neighbours.keys()

    def get_id(self):
        return self.id
    
    def get_name(self):
        return self.name
    
    def get_port(self):
        return self.port
    
    def get_ip(self):
        return self.ip
    
    def get_visited(self):
        return self.visited
    
    def get_routingTable(self):
        return self.routingTable
    
    def get_distance(self):
        return self.distance

    def get_previous(self):
        return self.previous
    
    def set_visited(self,visited):
        self.visited = visited
    
    def set_distance(self,distance):
        self.distance = distance

    def set_previous(self,previous):
        self.previous = previous
    
    def get_neighbours(self):
        return self.neighbours

    def get_cost(self, neighbor):
        return self.neighbours[neighbor]