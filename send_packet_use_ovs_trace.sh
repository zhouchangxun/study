ovs-appctl ofproto/trace br0 '
in_port=65534,
dl_src=50:54:00:00:00:01,
dl_dst=00:00:00:00:ff:01,
ip,
nw_src=192.168.0.2,
nw_dst=11.0.0.2,
nw_proto=1,nw_ttl=64' -generate
