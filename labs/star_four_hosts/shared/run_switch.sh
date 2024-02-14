#!/bin/bash
simple_switch_grpc -i 1@eth0 -i 2@eth1 -i 3@eth2 -i 4@eth3 --no-p4 --thrift-port 9090 -- --grpc-server-addr 127.0.0.1:50051 --cpu-port 100
