#!/usr/bin/env python3
import argparse
import os
import sys
from time import sleep

import grpc

# Import P4Runtime lib from parent utils dir
import utils.p4runtime_lib.bmv2 as bmv2
import utils.p4runtime_lib.helper as helper
from utils.p4runtime_lib.error_utils import printGrpcError
from utils.p4runtime_lib.switch import ShutdownAllSwitchConnections

ENABLED_PORT  = [1,2,3,4]
TIMEOUT_SEC = 15

def main(p4info_file_path, bmv2_file_path, routing_info):
    # Instantiate a P4Runtime helper from the p4info file
    p4info_helper = helper.P4InfoHelper(p4info_file_path)

    try:
        # Create a switch connection object for s1 and s2;
        # this is backed by a P4Runtime gRPC connection.
        # Also, dump all P4Runtime messages sent to switch to given txt files.
        s1 = bmv2.Bmv2SwitchConnection(
            name='s1',
            address='127.0.0.1:50051',
            device_id=0,
            #proto_dump_file='/logs/s1-p4runtime-requests.txt'
        )

        # Send master arbitration update message to establish this controller as
        # master (required by P4Runtime before performing any other write operation)
        s1.MasterArbitrationUpdate()
        s1.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                   bmv2_json_file_path=bmv2_file_path)
        print ("Installed P4 Program using SetForwardingPipelineConfig on %s" % s1.name)
        
        # Add static routing table and arp table
        with open(routing_info, 'r') as f:
            for line in f:
                ip_mac_pair = line.split(',')
                prefix, prefix_len = ip_mac_pair[0].split('/')
                next_hop_ip = ip_mac_pair[1]
                next_hop_mac = ip_mac_pair[2]
                egress_mac = ip_mac_pair[3]
                egress_port = int(ip_mac_pair[4].strip('\n'))
                prefix_len = int(prefix_len)

                print ("Add routing table entry", prefix, prefix_len, next_hop_ip)
                # TODO: Add table entries to "MyIngress.ipv4_route"
                # They represent the prefix of dstIP to next hop IP mapping.
                # 1. Use p4info_helper's buildTableEntry() method to build a table_entry
                # 2. Add the table_entry to the switch by calling s1's WriteTableEntry() method
                
                print ("Add ARP table entry", next_hop_ip,next_hop_mac)
                # TODO: Add table entries to "MyIngress.arp_table"
                # They represent the next hop IP to dstMAC mapping.
                # 1. Use p4info_helper's buildTableEntry() method to build a table_entry
                # 2. Add the table_entry to the switch by calling s1's WriteTableEntry() method
                
                print ("Add MAC table entry", next_hop_mac, egress_port, egress_mac)
                # TODO: Add table entries to "MyIngress.dmac_forward"
                # They represent the dstMAC to egress port and MAC mapping.
                # 1. Use p4info_helper's buildTableEntry() method to build a table_entry
                # 2. Add the table_entry to the switch by calling s1's WriteTableEntry() method
    
    except KeyboardInterrupt:
        print(" Shutting down.")
    except grpc.RpcError as e:
        printGrpcError(e)

    ShutdownAllSwitchConnections()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    parser.add_argument('--p4info', help='p4info proto in text format from p4c',
                        type=str, action="store", required=True)
    parser.add_argument('--bmv2-json', help='BMv2 JSON file from p4c',
                        type=str, action="store", required=True)
    parser.add_argument('--routing-info', help='Routing info file',
                        type=str, action="store", required=True)
    
    args = parser.parse_args()

    if not os.path.exists(args.p4info):
        parser.print_help()
        print("\np4info file not found: %s\nHave you run 'make'?" % args.p4info)
        parser.exit(1)
    if not os.path.exists(args.bmv2_json):
        parser.print_help()
        print("\nBMv2 JSON file not found: %s\nHave you run 'make'?" % args.bmv2_json)
        parser.exit(1)
    if not os.path.exists(args.routing_info):
        parser.print_help()
        print("\nBMv2 JSON file not found: %s\nHave you run 'make'?" % args.bmv2_json)
        parser.exit(1)
    
    main(args.p4info, args.bmv2_json, args.routing_info)
