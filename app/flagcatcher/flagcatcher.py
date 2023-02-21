#!/bin/python3
import sys
import re
from scapy.all import *
from typing import List
import pdb

NAT=False


class FlagHit:
    packet:Packet
    def __init__(self, packet:Packet):
        self.packet = packet

    def understood(self):
        h=self.packet.haslayer
        return h('IP') and self.proto() != 'Unknown'
    def srcIp(self):
        return self.packet['IP'].src

    def srcPort(self):
        proto = self.proto()
        p = self.packet
        return p['UDP'].sport if proto=='UDP' else p['TCP'].sport if proto=='TCP' else -1

    def dstIp(self):
        return self.packet['IP'].dst

    def dstPort(self):
        proto = self.proto()
        p = self.packet
        return p['UDP'].dport if proto=='UDP' else p['TCP'].dport if proto=='TCP' else -1


    def proto(self):
        h = self.packet.haslayer
        return 'UDP' if h('UDP') else 'TCP' if h('TCP') else 'ICMP' if h('ICMP') else 'Unknown'

    def summary(self):
        if (not self.understood()):
            return "Not understood"
        return  f"Src {self.srcIp()}:{self.srcPort()} | Dst {self.dstIp()}:{self.dstPort()} | Proto {self.proto()} ";
    
class HitAnalysis:
    hit:FlagHit
    packets:List[Packet]

def analyze_pcap (filename:string, flagformat:bytes):
    packets = sniff(offline=filename)
    p : Packet
    hits:List[FlagHit] = []

    #Get all hits of a flag in pcap
    for p in packets:
         if (re.search(flagformat,bytes(p.payload))):
            hit = FlagHit(p)
            hits.append(hit)

    #Analyze each hit
    hit:FlagHit
    for hit in hits:
        analyze_hit(hit,packets)
        
def analyze_hit(hit:FlagHit, packets:PacketList):
    id = hit.packet['IP']
    sessions= list(packets.sessions().items())
   # pdb.set_trace()
    #==TCP==
    # 1. Find all packets in the hit's TCP session
    if (hit.proto()=="TCP"):
        #Find the hit's TCP session
        sesh = next(s for s in sessions if any(p==hit.packet for p in s[1]))
        print(sesh)
        pass  
    
    #==UDP==
    # Last N packets from same src IP/port


    #==ICMP==
    # Last N packets from same src IP
    

    #==NAT==
    # Last X packets in the NAT session of this packet




analyze_pcap("test.pcap", br"flag\{[a-zA-Z0-9_]{1,16}\}")