#!/usr/bin/python
# Copyright 2014 Kewal Panchputre, Varun Umesh
# panch013@umn.edu, umesh001@umn.edu
#
# This file is part of POX.
#
# POX is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# POX is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with POX. If not, see <http://www.gnu.org/licenses/>.
#

"""
This is a demonstration file that has switch implementations for
cellular offloading.


Mininet: sudo mn --custom <path to custom topology>/CustomTopology.py --topo CustomTopology --mac --controller remote
Command Line: ./pox.py log.level --DEBUG Offload_Controller3
"""
from pox.lib import packet
from pox.core import core
from pox.lib.util import dpidToStr
# import pox.openflow.libopenflow_01 as of
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr, IP_ANY, IP_BROADCAST

log = core.getLogger()

s1_dpid = 0
s2_dpid = 0
s3_dpid = 0
src_ip = ""
dst_ip = ""


# This is a method that will be invoked during connection up phase!
# I collect the ID of all the switches
# These ID's are used later to install Switch specific rules. 

def _handle_ConnectionUP(event):
    
    global s1_dpid,s2_dpid,s3_dpid
    print "Connection is up!"
    dpidToStr(event.connection.dpid)
    
    for m in event.connection.features.ports:
            if m.name == "s1-eth1":
                s1_dpid = event.connection.dpid
                print "s1_dpid=", s1_dpid
            elif m.name == "s2-eth1":
                s2_dpid = event.connection.dpid
                print "s2_dpid=", s2_dpid
            elif m.name == "s3-eth1":
                s3_dpid = event.connection.dpid
                print "s3_dpid=",s3_dpid
                
def _handle_PacketIn(event):
    global s1_dpid,s2_dpid,s3_dpid
    global src_ip, dst_ip
    packet = event.parsed
    if packet.type==packet.IP_TYPE:
        ip_packet = packet.payload
        src_ip = IPAddr(ip_packet.srcip)
        dst_ip = IPAddr(ip_packet.dstip)
        #print "This is IP in %d-----------------> %s" % (event.connection.dpid, src_ip)
    
    """
    Check if the switch is S1, if so install all the rules specific to S1.    
    """
    '''
    if event.connection.dpid==s1_dpid:
        print "These are rules for S1..."
        print "S1 %s" % src_ip
        #ip_packet = packet.payload
        msg = of.ofp_flow_mod()
        msg.idle_timeout = 100
        msg.hard_timeout = 100
        msg.match.dl_type = 0x0800
        #msg.match.nw_src = "10.0.0.1"
        #msg.match.dl_src = "00:00:00:00:00:01"
        # TODO: Check if src_ip is null and add a check accrodingly!!
        msg.match.nw_src = src_ip
        msg.actions.append(of.ofp_action_output(port=2))
        event.connection.send(msg)
        
        msg = of.ofp_flow_mod()
        msg.idle_timeout = 100
        msg.hard_timeout = 100
        msg.match.dl_type = 0x0800
        msg.match.nw_src = "10.0.0.2"
        msg.actions.append(of.ofp_action_output(port=1))
        event.connection.send(msg)   
    '''
        
    if event.connection.dpid==s2_dpid:
        print "These are rules for S2..."
        #packet = event.parsed
        #ip_packet = packet.payload        
        msg = of.ofp_flow_mod()
        msg.idle_timeout = 100
        msg.hard_timeout = 100
        msg.match.dl_type = 0x0800        
        msg.match.nw_src = src_ip
        #msg.match.nw_src = "10.0.0.1"
        #msg.match.dl_src = "00:00:00:00:00:01"
        msg.match.nw_dst = "10.0.0.2"
        msg.actions.append(of.ofp_action_nw_addr.set_src("10.0.0.20"))
        msg.actions.append(of.ofp_action_output(port=2))
        event.connection.send(msg)
        
        msg = of.ofp_flow_mod()
        msg.idle_timeout = 100
        msg.hard_timeout = 100
        msg.match.dl_type = 0x0800
        msg.match.nw_src = "10.0.0.2"
        msg.match.nw_dst = "10.0.0.20"
        #msg.actions.append(of.ofp_action_nw_addr.set_dst("10.0.0.1"))
        msg.actions.append(of.ofp_action_nw_addr.set_dst(src_ip))
        #msg.actions.append(of.ofp_action_output(port=1))
        msg.actions.append(of.ofp_action_output(port=3))
        #msg.actions.append(of.ofp_action_output(port=of.OFPP_ALL))
        event.connection.send(msg)
              
        
    elif event.connection.dpid==s3_dpid:
        
         # Delete The Rules present on S1
        
        msg = of.ofp_flow_mod(command=of.OFPFC_DELETE)
        core.openflow.sendToDPID(s1_dpid,msg)
        
        # Copy the Rules from S1 to S3
        print "These are rules for S3..."
        #ip_packet = packet.payload
        msg = of.ofp_flow_mod()
        msg.idle_timeout = 100
        msg.hard_timeout = 100
        msg.match.dl_type = 0x0800
        #msg.match.nw_src = "10.0.0.1"
        #msg.match.dl_src = "00:00:00:00:00:01"
        msg.match.nw_src = src_ip
        msg.actions.append(of.ofp_action_output(port=1))
        event.connection.send(msg)
        
        msg = of.ofp_flow_mod()
        msg.idle_timeout = 100
        msg.hard_timeout = 100
        msg.match.dl_type = 0x0800
        msg.match.nw_src = "10.0.0.2"
        msg.actions.append(of.ofp_action_output(port=2))
        event.connection.send(msg)
        
    
def launch ():
    core.openflow.addListenerByName("ConnectionUp",_handle_ConnectionUP)
    core.openflow.addListenerByName("PacketIn",_handle_PacketIn)
