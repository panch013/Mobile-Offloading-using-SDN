"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch(LTE) --- switch(GW) --- host
     |                          |
      ----- switch(WiFi)-------- 
 
Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo

class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        leftHost = self.addHost( 'h1' )
        rightHost = self.addHost( 'h2' )
        lteSwitch = self.addSwitch( 's1' )
        gwSwitch = self.addSwitch( 's2' )
        wifiSwitch = self.addSwitch( 's3' )

        # Add links
        self.addLink( leftHost, lteSwitch )
        self.addLink( lteSwitch, gwSwitch )
        self.addLink( gwSwitch, rightHost )
        self.addLink( gwSwitch, wifiSwitch )
        self.addLink( leftHost, wifiSwitch )


topos = { 'oltopo': ( lambda: MyTopo() ) }
