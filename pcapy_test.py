# -*- coding: utf-8 -*-
# <nbformat>2</nbformat>

# <codecell>

import pcapy
dir(pcapy)

# <codecell>

pcapy.findalldevs()

# <codecell>

pc = pcapy.open_live('wlan0', 1024, False, 100)

# <codecell>

pc.setfilter('tcp and port 80')

from impacket.ImpactDecoder import *
# callback for received packets
def recv_pkts(hdr, data):
  packet = EthDecoder().decode(data)
  print packet
 
packet_limit = -1 # infinite
packet_limit = 10
pc.loop(packet_limit, recv_pkts) # capture packets

# <codecell>


