from NetworkMap import network
import Packet

import time
import sys, getopt
import threading

from socket import socket, AF_INET, SOCK_DGRAM

class Router():
    def __init__(self,name,ip,id,port,routingTable,initial,ttl = 7,waitTime=5):
        self.name = name
        self.ip = ip
        self.id = int(id)
        self.port = int(port)
        self.routingTable = routingTable
        self.initial = initial
        self.ttl = int(ttl)
        self.sentPackets = []
        self.dynamic = False
        self.waitTime = waitTime
    
    """
    A method to send packets to the correct interface/gateway while still reciving packet using threading
    """
    def handle_sending(self,packet,nextHop):
        s = socket (AF_INET, SOCK_DGRAM)
        print(f"\nRouter ({self.id}) Sent : ",Packet.print_packet(packet)," To : ",nextHop)   
        s.sendto(packet, nextHop)   
        s.close()

    """
    A method to start listning for all UDP packets recived and handling them
        Create a new Thread for sending/handling them and send/forward the packet 
    """
    def recive_and_handle_packets(self):
        s = socket(AF_INET, SOCK_DGRAM)
        s.bind((self.ip,self.port)) # start to listen for packets
        print(f"[x] Router ({self.id}) Reciving Packet on ",s.getsockname(),"\n")

        while True:
            self.handle_retransmit()
            packet, addr = s.recvfrom(1024)

            print(f"\nRouter ({self.id}) Received : ",Packet.print_packet(packet)," From : ",addr)

            self.handle_packet(packet)
        
        s.close()
    
    def handle_retransmit(self):
        for pkt in self.sentPackets:
            if time.time() - pkt[0] > self.waitTime:
                for packet in pkt[1]:
                    print(f"\nRouter ({self.id}) Did NOT Recieve ACK for {packet} In Time")
                    self.sentPackets.remove(pkt)
                    thread = threading.Thread(target=self.handle_packet(packet))
                    thread.start()
                    thread.join()

    
    def handle_packet(self,packet):
        pkt_type = packet [0]

        if pkt_type == Packet.UNICAST:
            self.handle_Unicast_packet(packet)
        
        elif pkt_type == Packet.MULTICAST:
            self.handle_Multicast_packet(packet)

        elif pkt_type == Packet.TUNNEL:
            self.handle_Tunnel_packet(packet)
            
        elif pkt_type == Packet.ACK:
            self.handle_Ack_Packet(packet)
    
    def handle_Unicast_packet(self,packet):
        pkt_type,seq,ttl,src,dst = Packet.read_header(packet)
                
        if ttl<=0 : # Drop Expired Packets
            return

        if self.id != dst:
            packet = bytearray(packet)
            packet[2] = packet[2] - 1  # reduce ttl

            nextHop = self.get_nextHop(dst)

            if nextHop != None:
                thread = threading.Thread(target=self.handle_sending(packet,nextHop))
                thread.start()
                thread.join()
            else:
                print(f"{dst} is not reachable from {self.id}")
        else:
            #Create a Reply
            dst = src
        
            ack_packet = Packet.create_Ack_Packet(Packet.ACK,seq,self.id,dst)
            
            nextHop = self.get_nextHop(dst)
            if nextHop != None:
                thread = threading.Thread(target=self.handle_sending(ack_packet,nextHop))
                thread.start()
                thread.join()
            else:
                print(f"{dst} is not reachable from {self.id}")

    """
    Not behaving properly when Tunneling to inital rp which turns out to be dynamic rp. As the router does not know it is dynamic 
    and thinks it intial at first. Thus, dynmaic is calcualted twice. First by the router that recieves the multicast 
    and once more by intial RP which turn out to be dynamic.  
    """
    def handle_Multicast_packet(self,packet):
        pkt_type,seq,ttl,k,src,destinations = Packet.read_header(packet)
        
        if ttl <= 0:
            return

        # Create ACK
        ############################################################################## 
        ack_packet = Packet.create_Ack_Packet(Packet.ACK,seq,self.id,src)
        
        nextHop = self.get_nextHop(src)
        if nextHop != None:
            thread = threading.Thread(target=self.handle_sending(ack_packet,nextHop))
            thread.start()
            thread.join()
        else:
            print(f"{src} is not reachable from {self.id}")
        #################################################################################

        option = -1
        time.sleep(0.5)
        print("\nTwo (2) options to send mutlicast packet from router :-")
        print("    1. Tunnel Multicast Packet to Initial RP")
        print("    2. Tunnel Multicast Packet to Dynamic RP (Not Working Fully Don't Use)")

        while option < 0  or option > 1:
            option = int(input("Choose an option : "))
            if option < 0  or option > 1:
                print("\n Incorrect Option. Please Try Again !!!\n")  
        print()

        packet = bytearray(packet)
        packet[2] = packet[2] - 1

        if option == 1:
            # Tunnel it to Initial
            dst = self.initial.get_id()
            tunnel_pkt = Packet.create_Tunnel_Packet(Packet.TUNNEL,seq,self.ttl,self.id,dst,packet)

            if self.id == dst:
                print(f"\nRouter ({self.id}) is Initial RP Itself")
                self.handle_packet(tunnel_pkt)
                return
            
            nextHop = self.get_nextHop(dst)

            if nextHop != None:
                thread = threading.Thread(target=self.handle_sending(tunnel_pkt,nextHop))
                self.sentPackets.append([time.time(),[tunnel_pkt],None,0]) # Save the sent packet to check for ACKs
                thread.start()
                thread.join()
            else:
                print(f"{dst} is not reachable from {self.id}")

        if option == 2:
            # Tunnel it to Dyanmic
            dynamic_rp_id,min_distance_dst_comb,min_distance = network.get_dynamic_RP_id(src,destinations,k)

            print("\nDynamic RP ID : ",dynamic_rp_id)
            print("Destination Combination : ", min_distance_dst_comb)
            print("Min Avg. Distance : ", min_distance,"\n")

            for dst in destinations:
                if dst not in min_distance_dst_comb:
                        min_distance_dst_comb.append(dst) # Still keep all destination in case one is not reachable

            msg = f"Send Unicast packet to {min_distance_dst_comb} From Dynamic"

            multicast_pkt = Packet.create_Multicast_Packet(Packet.MULTICAST,seq,ttl-1,k,src,min_distance_dst_comb,msg)
            tunnel_pkt = Packet.create_Tunnel_Packet(Packet.TUNNEL,0,self.ttl,self.id,dynamic_rp_id,multicast_pkt)

            if self.id == dynamic_rp_id:
                print(f"\nRouter ({self.id}) is Dynamic RP Itself")
                self.dynamic = True
                self.handle_packet(tunnel_pkt)
                return

            nextHop = self.get_nextHop(dynamic_rp_id)
            if nextHop:
                thread = threading.Thread(target=self.handle_sending(tunnel_pkt,nextHop))
                self.sentPackets.append([time.time(),[tunnel_pkt],None,0]) # Save the sent packet to check for ACKs
                thread.start()
                thread.join()

            else:
                print(f"{dynamic_rp_id} is not reachable from {self.id}")
    
        

        

    def handle_Tunnel_packet(self,packet):
        pkt_type,seq,ttl,src,dst = Packet.read_header(packet)

        if ttl <=0 : # Drop Packet
            return

        if self.id == dst:

            mult_packet = Packet.read_data(packet)
            pkt_type,seq_m,ttl_m,k,src_m,destinations = Packet.read_header(mult_packet)

            if (not self.dynamic) and (src != dst) and (self != src):
                # Create ACK
                ############################################################################## 
                ack_packet = Packet.create_Ack_Packet(Packet.ACK,seq,self.id,src)
                
                nextHop = self.get_nextHop(src)
                if nextHop != None:
                    thread = threading.Thread(target=self.handle_sending(ack_packet,nextHop))
                    thread.start()
                    thread.join()
                else:
                    print(f"{src} is not reachable from {self.id}")
                #################################################################################
            
            # IF Initial Router find dynamic and tunnel to Dynamic
            if self.initial.get_id() == self.id and not self.dynamic:

                time.sleep(0.5)
                dynamic_rp_id,min_distance_dst_comb,min_distance = network.get_dynamic_RP_id(src_m,destinations,k)

                print("\nDynamic RP ID : ",dynamic_rp_id)
                print("Destination Combination : ", min_distance_dst_comb)
                print("Min Avg. Distance : ", min_distance,"\n")

                for dst in destinations:
                    if dst not in min_distance_dst_comb:
                            min_distance_dst_comb.append(dst)

                msg = f"Send Unicast packet to {min_distance_dst_comb} From Dynamic"

                multicast_pkt = Packet.create_Multicast_Packet(Packet.MULTICAST,seq_m,ttl_m,k,src_m,min_distance_dst_comb,msg)
                tunnel_pkt = Packet.create_Tunnel_Packet(Packet.TUNNEL,seq,self.ttl,self.id,dynamic_rp_id,multicast_pkt) 
                
                if self.id == dynamic_rp_id:
                    print(f"\nRouter ({self.id}) is Dynamic RP Itself")
                    self.dynamic = True
                    self.handle_packet(tunnel_pkt)
                    return
                

                nextHop = self.get_nextHop(dynamic_rp_id)

                if nextHop != None:
                    thread = threading.Thread(target=self.handle_sending(tunnel_pkt,nextHop))            
                    thread.start()
                    self.sentPackets.append([time.time(),[tunnel_pkt],None,0]) # Save the sent packet to check for ACKs
                    thread.join()

                else:
                    print(f"{dst} is not reachable from {self.id}")
                

            else: # ELSE router is dynamic and send k unicast to destinations 
                self.dynamic = False # if dynamic changes next time
                for i in range(k):
                    dst = destinations[i]
                    nextHop = self.get_nextHop(dst)    
                    if nextHop != None:
                        msg = f"Unicast Packet To {dst}"
                        packet = Packet.create_Unicast_Packet(Packet.UNICAST,seq_m,self.ttl,self.id,dst,msg)
                        thread = threading.Thread(target=self.handle_sending(packet,nextHop))            
                        thread.start()
                        if i == 0:
                            self.sentPackets.append([time.time(),[packet],src_m,k]) # Save the sent packet to check for ACKs
                        else:
                            self.sentPackets[-1][1].append(packet)
                        
                        thread.join()
                    else:
                        print(f"{dst} is not reachable from {self.id}")

        else:
            packet = bytearray(packet)
            packet[2] = packet[2] - 1 
            nextHop = self.get_nextHop(dst)
            if nextHop != None:
                thread = threading.Thread(target=self.handle_sending(packet,nextHop))
                thread.start()
                thread.join()
            else:
                print(f"{dst} is not reachable from {self.id}")

    def handle_Ack_Packet(self, packet):
        pkt_type,seq_a,src_a,dst = Packet.read_header(packet)
        if self.id != dst:
            nextHop = self.get_nextHop(dst)
            if nextHop != None:
                thread = threading.Thread(target=self.handle_sending(packet,nextHop))
                thread.start()
                thread.join()
            else:
                print(f"{dst} is not reachable from {self.id}")
        else:
            for pkt in self.sentPackets:
                packet_lst = pkt[1]
                for packet in packet_lst:
                    pkt_type = packet [0]
                    
                    if pkt_type == Packet.UNICAST:
                        pkt_type,seq,ttl,src,dst = Packet.read_header(packet)
                        if src_a == dst and seq_a==seq:
                            print(f"\nRouter ({self.id}) reviced ACK For : {packet} From : {src_a}")
                            if pkt[-1] == 0:
                                self.sentPackets.remove(pkt)
                            elif pkt[-1] -1 <= 0:
                                print(f"\nRouter ({self.id}) reviced all ACKs For : {packet_lst}")
                                dst = pkt[-2]
                                ack_pkt = Packet.create_Ack_Packet(Packet.ACK,seq,self.id,dst)
                                nextHop = self.get_nextHop(dst)
                                if nextHop != None:
                                    thread = threading.Thread(target=self.handle_sending(ack_pkt,nextHop))
                                    thread.start()
                                    thread.join()
                                    self.sentPackets.remove(pkt)
                                else:
                                    print(f"{dst} is not reachable from {self.id}")
                            else : 
                                 pkt[-1] = pkt[-1] - 1
                    
                    elif pkt_type == Packet.MULTICAST:
                        pkt_type,seq,ttl,k,src,destinations = Packet.read_header(packet)

                    elif pkt_type == Packet.TUNNEL:
                        pkt_type,seq,ttl,src,dst = Packet.read_header(packet)
                        if src_a == dst and seq_a==seq:
                            print(f"\nRouter ({self.id}) reviced ACK For : {packet} From : {src_a}")
                            if pkt[-1] == 0:
                                self.sentPackets.remove(pkt)
                            elif pkt[-1] -1 <= 0:
                                print(f"\nRouter ({self.id}) reviced all ACKs For : {packet_lst}")
                                dst = pkt[-2]
                                ack_pkt = Packet.create_Ack_Packet(Packet.ACK,seq,self.id,dst)
                                nextHop = self.get_nextHop(dst)
                                if nextHop != None:
                                    thread = threading.Thread(target=self.handle_sending(ack_pkt,nextHop))
                                    thread.start()
                                    thread.join()
                                    self.sentPackets.remove(pkt)
                                else:
                                    print(f"{dst} is not reachable from {self.id}")
                            else : 
                                 pkt[-1] = pkt[-1] - 1
                    

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

def router_info(name,initial,ttl=7,waitTime=5):
    router = get_node_from_name(name)
    initial = get_node_from_name(initial)
    
    if router == None:
        print(f"Node ({name}) Not Found in Network")
        sys.exit()

    if initial == None:
        print(f"Initial Router ({initial}) Not Found in Network")
        sys.exit()

    return Router(router.get_name(),router.get_ip(),router.get_id(),router.get_port(),router.get_routingTable(),initial,ttl,waitTime)


def main(argv):

    name = None
    initial = None
    ttl = None
    waitTime = None

    opts, args = getopt.getopt(argv,"i:n:t:w:",["initial=","name=","ttl=","wait="])
    
    for opt, arg in opts:
        if opt in ['-i',"--initial"]:
            initial = arg
        elif opt in ['-n',"--name"]:
            name = arg
        elif opt in ['-t',"--ttl"]:
            ttl = arg
        elif opt in ['-w',"--wait"]:
            waitTime = float(arg)
        
    print("\nRouter Starting....")
    router = router_info(name,initial,ttl,waitTime)
    print("Router: name = ",router.name," id = ",router.id, " initial = ", router.initial.get_id())
    print("*Router Listnig For Packets")
    router.recive_and_handle_packets()


if __name__ == "__main__":
   main(sys.argv[1:])