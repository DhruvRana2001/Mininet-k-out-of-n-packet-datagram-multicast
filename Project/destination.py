from NetworkMap import network
import Packet

import time
import sys, getopt
import threading

from socket import socket, AF_INET, SOCK_DGRAM

class Receiver():
    def __init__(self,name,ip,id,port,routingTable):
        self.name = name
        self.ip = ip
        self.id = int(id)
        self.port = int(port)
        self.routingTable = routingTable
        
    
    """
    A method to send packets to the correct interface while stil reciving packet using threading
    packet : packet to send (created using the Packet file)
    """
    def send_Packet(self,packet,nextHop):
        pkt_type = packet [0]
        s = socket (AF_INET, SOCK_DGRAM)
        print(f"\nDestination ({self.id}) Sent : ",Packet.print_packet(packet)," To : ",nextHop)
        s.sendto(packet,nextHop)
        s.close()

    """
    A method to recieve packets and send reply to appropriate packets using threading
    A socket is binded and waits to recieve packets 
    """
    def recieve_packets(self):
        s = socket (AF_INET, SOCK_DGRAM)
        s.bind((self.ip, self.port))
        print("[x] Destination Reciving Packet on ",s.getsockname(),"\n")

        #Waits to receive packet
        while True:
            packet, addr = s.recvfrom(1024)
            print(f"\nDestination ({self.id}) Received : ",Packet.print_packet(packet)," From : ",addr)
            self.handle_packet(packet)
            
    
    def handle_packet(self,packet):
        pkt_type = packet [0]

        if pkt_type == Packet.UNICAST:
            self.handle_Unicast_packet(packet)
        
        elif pkt_type == Packet.MULTICAST:
            self.handle_Multiicast_packet(packet)

        elif pkt_type == Packet.TUNNEL:
            self.handle_Tunnel_packet(packet)
            
        elif pkt_type == Packet.ACK:
            self.handle_Ack_Packet(packet)
    
    def handle_Unicast_packet(self,packet):
        pkt_type,seq,ttl,src,dst = Packet.read_header(packet)
        
        # Create Reply
        dst = src
        
        ack_packet = Packet.create_Ack_Packet(Packet.ACK,seq,self.id,dst)
        
        nextHop = self.get_nextHop(dst)
        if nextHop != None:
            thread = threading.Thread(target=self.send_Packet(ack_packet,nextHop))
            thread.start()
            thread.join()
        else:
            print(f"{dst} is not reachable from {self.id}")
    
    def handle_Multiicast_packet(self,packet):
        pkt_type,seq,ttl,k,src,destinations = Packet.read_header(packet)

        # Send it back into network, Since destination cant handle mutlicast
        # Try to send to first neighbour (Works due to assumption host nodes are connected to only one router)
        first_neighbour = list(get_node_from_name(self.name).get_connections())[0]
    
        if first_neighbour :
            dst = first_neighbour.get_id()
            nextHop = self.get_nextHop(dst)
            if nextHop != None:
                thread = threading.Thread(target=self.send_Packet(packet,nextHop))
                thread.start()
                thread.join()
            else:
                print(f"{dst} is not reachable from {self.id}")
        else:
            print("Cannot Send a Multicast Packet")
        
    
    def handle_Tunnel_packet(self,packet):
        pkt_type,seq,ttl,src,dst = Packet.read_header(packet)
        mult_packet = Packet.read_data(packet)
        pkt_type,seq_m,ttl_m,k,src_m,destinations = Packet.read_header(mult_packet)

        # Create Reply
        dst = src
        
        ack_packet = Packet.create_Ack_Packet(Packet.ACK,seq,self.id,dst)
        
        nextHop = self.get_nextHop(dst)
        if nextHop != None:
            thread = threading.Thread(target=self.send_Packet(ack_packet,nextHop))
            thread.start()
            thread.join()
        else:
            print(f"{dst} is not reachable from {self.id}")
    
    def handle_Ack_Packet(self,packet):
        pkt_type,seq,src,dst = Packet.read_header(packet)
    
    def get_nextHop (self,dst):
        if self.routingTable[dst] != None:
                nextHop_Node = network.get_node_by_id(self.routingTable[dst][1][1])
                gateway = nextHop_Node.get_ip()
                port = nextHop_Node.get_port()
                return (gateway,port)
        return None

def get_node_from_name(name):
    for node in network:
        if(node.get_name() == name):
            return node
    return None

def receiver_info(name):
    destination = get_node_from_name(name)
    if destination == None:
        print(f"Node ({name}) Not Found in Network")
        sys.exit()
    return Receiver(destination.get_name(),destination.get_ip(),destination.get_id(),destination.get_port(),destination.get_routingTable())
    


def main(argv):

    name = None

    opts, _ = getopt.getopt(argv,"n:",["name="])
    
    for opt, arg in opts:
        if opt in ['-n',"--name"]:
            name = arg


    print("\nDestination Starting....")
    sender = receiver_info(name)
    print("Destination: name = ",sender.name," id = ",sender.id)
    print("*Destination Reciving Multicast Packet\n")
    sender.recieve_packets()


if __name__ == "__main__":
   main(sys.argv[1:])