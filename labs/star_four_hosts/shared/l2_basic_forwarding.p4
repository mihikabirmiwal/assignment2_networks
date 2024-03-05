/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<48> macAddr_t;
header ethernet_t {
    /* TODO: Define ethernet header*/ 
    bit<64> preamble;
    macAddr_t dest_macAddr;
    macAddr_t source_macAddr;
    bit<16> type;
}

/* digest format for mac learning*/
struct mac_learn_digest_t {
    /* TODO */ 
    macAddr_t addr;
    bit<16> port;
}

struct metadata {
    /* empty */
}

struct headers {
    ethernet_t ethernet;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        packet.extract(hdr.ethernet);
        transition accept;
    }
}


/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    /* define actions */
    action drop() {
        mark_to_drop(standard_metadata);
    }

    action NoAction() {
        
    }

    action forward_to_port(bit<9> egress_port) {
        standard_metadata.egress_spec = egress_port;
    }

    action broadcast() {
        standard_metadata.mcast_grp = (bit<16>) standard_metadata.ingress_port; 
    }
    /* learn() sends srcMAC to ingress port mapping to the controller */
    /* The controller should update the both smac_table entry and dmac_entry*/
    action learn() {
        mac_learn_digest_t mac_learn_msg;
        /* TODO: Fill the digest message with srcMAC and ingress port */
        mac_learn_msg.addr = hdr.ethernet.source_macAddr;
        mac_learn_msg.port = (bit<16>) standard_metadata.ingress_port;
        /* send the digest message to the controller */
        digest<mac_learn_digest_t>(1, mac_learn_msg);
    }

    /* define forwarding table */
    table dmac_forward {
        /* TODO: define key, actions, and default action for the table */ 
        size = 4;
        support_timeout = true;
        key = {
            hdr.ethernet.dest_macAddr: exact;
        }

        actions = {
            forward_to_port;
            broadcast;
        }

        default_action = broadcast();
    }

    /* check if the mac address to port mapping exists */
    table smac_table{
        /* TODO: define key, actions, and default action for the table */  
        size = 4;
        support_timeout = true;
        key = {
            hdr.ethernet.source_macAddr: exact;
        }

        actions = {
            NoAction;
            learn;
        }

        default_action = learn();
    }

    /* applying tables */
    apply {
        smac_table.apply();
        dmac_forward.apply();
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {


    apply {  }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
     apply {

    }
}


/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

//switch architecture
V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
