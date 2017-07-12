#!/bin/bash

# Create the first logical switch with one port
ovn-nbctl ls-add sw0
ovn-nbctl lsp-add sw0 sw0-port1
ovn-nbctl lsp-set-addresses sw0-port1 "50:54:00:00:00:01 192.168.0.2"

# Create the second logical switch with one port
ovn-nbctl ls-add sw1
ovn-nbctl lsp-add sw1 sw1-port1
ovn-nbctl lsp-set-addresses sw1-port1 "50:54:00:00:00:03 11.0.0.2"

# Create a logical router and attach both logical switches
ovn-nbctl lr-add lr0
ovn-nbctl lrp-add lr0 lrp0 00:00:00:00:ff:01 192.168.0.1/24
ovn-nbctl lsp-add sw0 lrp0-attachment
ovn-nbctl lsp-set-type lrp0-attachment router
ovn-nbctl lsp-set-addresses lrp0-attachment 00:00:00:00:ff:01
ovn-nbctl lsp-set-options lrp0-attachment router-port=lrp0
ovn-nbctl lrp-add lr0 lrp1 00:00:00:00:ff:02 11.0.0.1/24
ovn-nbctl lsp-add sw1 lrp1-attachment
ovn-nbctl lsp-set-type lrp1-attachment router
ovn-nbctl lsp-set-addresses lrp1-attachment 00:00:00:00:ff:02
ovn-nbctl lsp-set-options lrp1-attachment router-port=lrp1

# View a summary of the configuration
ovn-nbctl show

# Create ports on the local OVS bridge, br-int.  When ovn-controller
# sees these ports show up with an "iface-id" that matches the OVN
# logical port names, it associates these local ports with the OVN
# logical ports.  ovn-controller will then set up the flows necessary
# for these ports to be able to communicate each other as defined by
# the OVN logical topology.
#ovs-vsctl add-port br-int sw0-port1 -- set Interface sw0-port1 external_ids:iface-id=sw0-port1
#ovs-vsctl add-port br-int sw1-port1 -- set Interface sw1-port1 external_ids:iface-id=sw1-port1
