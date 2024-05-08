import Topo
import cleanup

import sys
import time

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.clean import cleanup as clean

def prompt(hosts : list, routers : list):
    MAX_N = len(hosts) - 1

    i = 1
    n = -1
    k = -1
    TTL = -1
    waitTime = -1
    src = None
    initial_RP = None
    dst = []

    while n <= 0 or n > MAX_N: # max N : 3
        n = int(input("\nTotal Destination Nodes (N) : "))
        if n <=0 :
            print("N must be grater than 0")
        elif n > MAX_N:
            print(f"N must be less than or equal to {MAX_N}")
        
    print("N = ", n)

    while k <=0 or k>n:
        k = int(input("\nMin Destination Nodes (K) : "))
        if k <=0 :
            print("K must be grater than 0")
        elif k > n:
            print(f"N must be less than or equal to {n}")

    print("k = ", k)

    while TTL <=0:
        TTL = int(input("\nMax Hops (TTL) : "))
        if TTL <=0 :
            print("TTL must be grater than 0")

    print("TTL = ", TTL)

    while waitTime <=0:
        waitTime = float(input("\nWait Time (sec) : "))
        if waitTime <=0 :
            print("Wait Time must be grater than 0")

    print("Wait Time = ", waitTime)

    while initial_RP == None or initial_RP not in routers:
        initial_RP = input(f"\nInitial RP {routers} : ")
        if (initial_RP not in routers):
            print(f"Initial RP must be from {routers}")

    print("Initial RP = ",initial_RP)

    while src == None or src not in hosts:
        src = input(f"\nSender Node {hosts} : ")
        if (src not in hosts):
            print(f"Sender must be from {hosts}")

    print("Sender = ",src)

    while len(dst) < n:
        hosts = [host for host in hosts if host not in src]

        if n == MAX_N:
            print()
            dst = hosts
            break

        host = input(f"\nDestination {i} Node {hosts} : ")
        if (host not in hosts):
            print(f"Destination(s) must be from {hosts}")
            continue
        dst.append(host)
        i += 1
        

    print("Destination(s) = ",dst,"\n")

    return n,k,initial_RP,src,dst,TTL,waitTime


def K_out_N_multicast(net : Mininet):
    
    # Using custom cls makes it so we dont have to maually list hosts and routers of topology
    # Thus custom cls in topology is preferred as it doe not change much and allows us to make the topology with releveant info all in one file
    hosts= ["S", "d1", "d2", "d3"]
    routers = ['r1','r2','r3','r4','r5','r6','r7']
    

    try:
        hosts_lst = [node.name for node in net.values() if type(node) == Topo.Host]
        
        if len(hosts_lst) == 0:
            hosts_lst = hosts
            print("Not Using Custom CLS Please Ensure That You Create a Dict And Use That To Initalize The Network Graph")
            print("Also Ensure A List of Hosts and Routers Is Created")
        else:
            hosts = hosts_lst
            
        routers_lst = [node.name for node in net.values() if type(node) == Topo.Router]
        
        if len(routers_lst) == 0:
            routers_lst = routers
            print("Not Using Custom CLS Please Ensure That You Create a Dict And Use That To Initalize The Network Graph")
            print("Also Ensure A List of Hosts and Routers Is Created")
        else:
            routers = routers_lst

    except:
        print("Not Using Custom CLS Please Ensure That You Create a Dict And Use That To Initalize The Network Graph")
        print("Also Ensure A List of Hosts and Routers Is Created")

    n,k,initial_RP,src,dst,TTL,waitTime = prompt(hosts,routers)

    # Since we dont have gateways add route to neigbours so they can be reached
    for link in net.links:
        link.intf1.node.cmd(f"ip route add {link.intf2.node.IP()} dev {link.intf1}")
        link.intf2.node.cmd(f"ip route add {link.intf1.node.IP()} dev {link.intf2}")
    

    routers_thread = []
    for r in routers:
        router = net[r].popen(f"python3 router.py --name {r} --initial {initial_RP} --ttl {TTL} --wait {waitTime}",stdout=sys.stdout,stderr=sys.stderr,stdin=sys.stdin)
        routers_thread.append(router)
        time.sleep(0.5)
    
    destinations_thread = []
    for i in dst:
        destination = net[i].popen(f"python3 destination.py --name {i}",stdout=sys.stdout,stderr=sys.stderr,stdin=sys.stdin)
        destinations_thread.append(destination)
        time.sleep(0.5)

    source  = net[src].popen(f"python3 source.py --name {src} --initial {initial_RP} --kval {k} --ttl {TTL} --wait {waitTime} --dst {','.join(dst)}",stdout=sys.stdout,stderr=sys.stderr,stdin=sys.stdin)
    time.sleep(4)
    source.wait()
    

    
def MakeTopo():
    topo = Topo.topology( )
    net = Mininet(topo,controller=None)

    net.start()
    K_out_N_multicast(net)
    CLI(net) # for more debugging
    net.stop()


if __name__ == '__main__':	
    clean()
    setLogLevel('info')	
    MakeTopo()
    clean()
    cleanup.cleanup()