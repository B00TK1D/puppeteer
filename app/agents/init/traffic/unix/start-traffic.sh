#!/bin/sh

rm -f /tmp/traffic.pcap /tmp/traffic.pcap.gz

# Start infinite loop of tcpdump dumping to /tmp/traffic.pcap every 10 seconds
while true; do
  timeout 10.1 tcpdump -G 10 -w /tmp/traffic.pcap not port $2
  # gzip the pcap file
  gzip -f /tmp/traffic.pcap
done