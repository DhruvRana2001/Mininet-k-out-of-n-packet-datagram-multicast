from NetworkMap import network
import Packet

import time
import sys, getopt
import threading

from socket import socket, AF_INET, SOCK_DGRAM

class Source():
    def __init__(self,name,ip,id,port,routingTable,k,initial,dst,ttl = 7,waitTime = 5):
        self.name = name
        self.ip = ip
        self.id = int(id)
        self.port = int(port)
        self.routingTable = routingTable
        self.k = int(k)
        self.initial = initial
        self.dst = dst
        self.ttl = int(ttl)
        self.waitTime = waitTime
        self.sentPackets = []
    
    """
    A method to send packets to the correct interface while stil reciving packet using threading
    packet : packet to send (created using the Packet file)
    """
    def handle_sending_Packet(self,packet):
        pkt_type = packet [0]

        if pkt_type == Packet.UNICAST:
            pkt_type,seq,ttl,src,dst = Packet.read_header(packet)
            nextHop = self.get_nextHop(dst)
            if nextHop != None:
                s = socket (AF_INET, SOCK_DGRAM) 
                print(f"Sender Sending : {Packet.print_packet(packet)} To : {nextHop}")
                s.sendto(packet,nextHop)
                s.close()
            else:
                print(f"{dst} is not reachable from {self.id}")
        
        elif pkt_type == Packet.MULTICAST:
            pkt_type,seq,ttl,k,src,dst = Packet.read_header(packet)
            
            # Try to send to first neighbour (Works due to assumption host nodes are connected to only one router)
            first_neighbour = list(get_node_from_name(self.name).get_connections())[0]
        
            if first_neighbour :
                dst = first_neighbour.get_id()
                nextHop = self.get_nextHop(dst)
                if nextHop != None:
                    s = socket (AF_INET, SOCK_DGRAM) 
                    print(f"Sender Sending : {Packet.print_packet(packet)} To : {nextHop}")
                    s.sendto(packet,nextHop)
                    s.close()
                else:
                    print(f"{dst} is not reachable from {self.id}")
            else:
                print("Cannot Send a Multicast Packet")
                

        
        elif pkt_type == Packet.TUNNEL:
            pkt_type,seq,ttl,src,dst = Packet.read_header(packet)
            nextHop = self.get_nextHop(dst)
            if nextHop != None:
                s = socket (AF_INET, SOCK_DGRAM) 
                print(f"Sender Sending : {Packet.print_packet(packet)} To : {nextHop}")
                s.sendto(packet,nextHop)
                s.close()
            else:
                print(f"{dst} is not reachable from {self.id}")

        elif pkt_type == Packet.ACK:
            pkt_type,seq,src,dst = Packet.read_header(packet)
            nextHop = self.get_nextHop(dst)
            if nextHop != None:
                s = socket (AF_INET, SOCK_DGRAM) 
                print(f"Sender Sending : {Packet.print_packet(packet)} To : {nextHop}")
                s.sendto(packet,nextHop)
                s.close()
            else:
                print(f"{dst} is not reachable from {self.id}")
    
        
    def get_nextHop (self,dst):
        if self.routingTable[dst] != None:
                nextHop_Node = network.get_node_by_id(self.routingTable[dst][1][1])
                gateway = nextHop_Node.get_ip()
                port = nextHop_Node.get_port()
                return (gateway,port)
        return None

    """
    A method to Send Multicast/Unicast packet 
    Create a new Thread for sending/handling them and send/forward the packet 
    """
    def send_packet(self):
        s = socket (AF_INET, SOCK_DGRAM)
        s.bind((self.ip, self.port))
        print("[x] Sender Reciving Packet on ",s.getsockname(),"\n")

        seq_num = 0
        sent = False

        # if 1 dst send unicast
        if len(self.dst) == 1:
            dst = self.dst[0]
            packet = Packet.create_Unicast_Packet(Packet.UNICAST,seq_num,self.ttl,self.id,int(dst),f"Unicast To {dst}")
            num_of_ack = 1

        else:
            option = -1
            print("\nTwo (2) options to send mutlicast packet from router :-")
            print("    1. Send Multicast Packet")
            print("    2. Tunnel Multicast Packet to Initial RP")

            while option < 0  or option > 2:
                option = int(input("Choose an option : "))
                if option < 0  or option > 2:
                    print("\n Incorrect Option. Please Try Again !!!\n")  
            print()  
            # Create the Multicast Packet
            num_of_ack = 2
            dst_lst = ",".join([str(x) for x in self.dst])
            msg = f"Multicast to best {self.k} destination(s) from {dst_lst}"

            multicast_pkt = Packet.create_Multicast_Packet(Packet.MULTICAST,seq_num,self.ttl,self.k,int(self.id),self.dst,msg)
            if option == 1:
                packet = multicast_pkt
            
            elif option == 2:
            # Create a Tunnel Packet to Initial RP
                packet = Packet.create_Tunnel_Packet(Packet.TUNNEL,seq_num,self.ttl,self.id,self.initial.get_id(),multicast_pkt)
                
        print(packet)
        self.handle_sending_Packet(packet)
 
        self.sentPackets.append([time.time(),[packet],None,num_of_ack])

        while True:
            if len(self.sentPackets) == 0:
                break
            self.handle_retransmit()
            packet, addr = s.recvfrom(1024)
            print(f"\nSender ({self.id}) Received : ",Packet.print_packet(packet)," From : ",addr)
            self.handle_packets(packet)
        print()

    def handle_retransmit(self):
        for pkt in self.sentPackets:
            if time.time() - pkt[0] > self.waitTime:
                for packet in pkt[1]:
                    print(f"\nSender ({self.id}) Did NOT Recieve ACK for {packet} In Time")
                    self.sentPackets.remove(pkt)
                    thread = threading.Thread(target=self.handle_sending_Packet(packet))
                    thread.start()
                    thread.join()

    def handle_packets(self,packet):
        pkt_type = packet[0]
        if pkt_type == Packet.ACK:
            self.handle_Ack_Packet(packet)
    
    def handle_Ack_Packet(self, packet):
        pkt_type,seq_a,src_a,dst = Packet.read_header(packet)
        if self.id != dst:
            return
        
        #We Are only sending one datagram/packet
        #thus all acks recived will go towards that packet
        for pkt in self.sentPackets:
            packet_lst = pkt[1]
            for packet in packet_lst:
                pkt_type = packet [0]
                
                if pkt_type == Packet.UNICAST:
                    pkt_type,seq,ttl,src,dst = Packet.read_header(packet)
                    
                    if src_a == dst and seq_a==seq:
                        print(f"\nSender ({self.id}) reviced ACK For : {packet} From : {src_a}")
                        
                        if pkt[-1] == 0:
                            self.sentPackets.remove(pkt)
                        elif pkt[-1] -1 <= 0:
                            print(f"\nSender ({self.id}) reviced all ACKs For : {packet_lst}")        
                            self.sentPackets.remove(pkt)
                        else : 
                            pkt[-1] = pkt[-1] - 1

                elif pkt_type == Packet.TUNNEL:
                    pkt_type,seq,ttl,src,dst = Packet.read_header(packet)
                    
                    if seq_a==seq:
                        print(f"\nSender ({self.id}) reviced ACK For : {packet} From : {src_a}")
                        
                        if pkt[-1] == 0:
                            self.sentPackets.remove(pkt)
                        elif pkt[-1] -1 <= 0:
                            print(f"\nSender ({self.id}) reviced all ACKs For : {packet_lst}")
                            self.sentPackets.remove(pkt)
                        else : 
                            pkt[-1] = pkt[-1] - 1
                
                elif pkt_type == Packet.MULTICAST:
                    pkt_type,seq,ttl,k,src,destinations = Packet.read_header(packet)
                    
                    if seq_a == seq:
                        print(f"\nSender ({self.id}) reviced ACK For : {packet} From : {src_a}")
                        if pkt[-1] == 0:
                            self.sentPackets.remove(pkt)
                        elif pkt[-1] -1 <= 0:
                            print(f"\nSender ({self.id}) reviced all ACKs For : {packet_lst}")
                            self.sentPackets.remove(pkt)
                        else : 
                            pkt[-1] = pkt[-1] - 1
                            
            

            

def get_node_from_name(name):
    for node in network:
        if(node.get_name() == name):
            return node
    return None

def sender_info(name,k,initial,dst,ttl,waitTime):
    sender = get_node_from_name(name)
    initial = get_node_from_name(initial)
    if sender == None:
        print(f"Node ({name}) Not Found in Network")
        sys.exit()
    if initial == None:
        print(f"Initial Router ({initial}) Not Found in Network")
        sys.exit()
    return Source(sender.get_name(),sender.get_ip(),sender.get_id(),sender.get_port(),sender.get_routingTable(),k,initial,dst,ttl,waitTime)
    

def main(argv):

    name = None
    k = None
    initial = None
    dst = None
    waitTime = None


    opts, _ = getopt.getopt(argv,"n:k:i:d:t:w:",["name=","kval=","initial=","dst=","ttl=","wait="])
    
    for opt, arg in opts:
        if opt in ['-n',"--name"]:
            name = arg

        elif opt in ['-k',"--kval"]:
            k = arg

        elif opt in ['-i',"--initial"]:
            initial = arg
        
        elif opt in ['-d',"--dst"]:
            dst = arg
        
        elif opt in ['-t',"--ttl"]:
            ttl = arg
        
        elif opt in ['-w',"--wait"]:
            waitTime = float(arg)

    # conver dst to id
    if not dst == None:
        dst = dst.split(",")
        dst = [get_node_from_name(x).get_id() for x in dst]

    print("\nSender Starting....")
    sender = sender_info(name,k,initial,dst,ttl,waitTime)
    print("Sender: name = ",sender.name," id = ",sender.id)
    print("*Sender Sending Multicast Packet")
    print("     Initial RP = ",sender.initial.get_id()," dst = ",sender.dst)
    sender.send_packet()

if __name__ == "__main__":
   main(sys.argv[1:])