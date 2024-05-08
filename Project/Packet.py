import struct

UNICAST = 1
MULTICAST = 2
TUNNEL = 3
ACK = 4


"""
A method that creates a multicast packet
"""
def create_Multicast_Packet(pkt_type,seq,ttl,k,src,dst,data):
    n = len(dst) # Had to add n so header size can change dynamically
    header = struct.pack(f'BBBBBB{n}B',pkt_type,seq,ttl,k,n,src,*dst)
    return header + bytes(data,'utf-8')

"""
A method that creates a multicast packet
"""
def create_Unicast_Packet(pkt_type,seq,ttl,src,dst,data):
    header = struct.pack(f'BBBBB',pkt_type,seq,ttl,src,dst)
    return header + bytes(data,'utf-8')

"""
A method that creates a tunnel packet
"""
def create_Tunnel_Packet(pkt_type,seq,ttl,src,dst,multicast_pkt):
    header = struct.pack(f'BBBBB',pkt_type,seq,ttl,src,dst)
    return header + multicast_pkt
"""
A method that creates a ack packet
"""
def create_Ack_Packet(pkt_type,seq,src,dst):
    header = struct.pack(f'BBBB',pkt_type,seq,src,dst)
    return header


"A method to extract and unpack the header of a encapsulated packet"
def read_header(pkt):
    pkt_type = pkt [0]

    if pkt_type == UNICAST:
        header = pkt[0:5]
        pkt_type,seq,ttl,src,dst = struct.unpack(f'BBBBB',header)
        return int(pkt_type),int(seq),ttl,int(src),int(dst)
    
    elif pkt_type == MULTICAST:
        header = pkt[0: (6 + pkt[4])]
        destinations = []
        pkt_type,seq,ttl,k,n,src,*destinations = struct.unpack(f'BBBBBB{pkt [4]}B',header)
        dst = [int(d) for d in destinations]
        return int(pkt_type),int(seq),ttl,int(k),int(src),list(dst)

    elif pkt_type == TUNNEL:
        header = pkt[0:5]
        pkt_type,seq,ttl,src,dst = struct.unpack(f'BBBBB',header)
        return int(pkt_type),int(seq),ttl,int(src),int(dst)

    elif pkt_type == ACK:
        header = pkt[0:4]
        pkt_type,seq,src,dst = struct.unpack(f'BBBB',header)
        return int(pkt_type),int(seq),int(src),int(dst)


"A method to extract data from a encapsulated packet"
def read_data(pkt):
    pkt_type = pkt [0]
    data = None

    if pkt_type == UNICAST:
        data = pkt[5:].decode('utf-8')
    
    elif pkt_type == MULTICAST:
        data = pkt[(6 + pkt[4]):].decode('utf-8')

    elif pkt_type == TUNNEL:
        data = pkt[5:]

    elif pkt_type == ACK:
        data = None
    
    return data

"A method to print packet"
def print_packet(pkt):
    data = read_data(pkt)
    if data == None:
        return read_header(pkt)
    else:
        return f"{read_header(pkt)} {data}"