To execute:<br/>
(1) Run 'python3 Router.py'<br/>
(2) Open new terminal and run 'python3 Router2.py'<br/>
(3) Open new terminal and Run 'python3 NodeDriver.py'<br/><br/>
Current Node messages supported by RouterListener:<br/>
(1) REGISTER - Requests the router on the home network to register the node with the HA. Node receives a newly allocated IP address.<br/>
(2) REGISTER FOREIGN - Requests the router on foreign network to register the node with the foreign HA. Node receives a new Care of Address (CoA). The node's HA on its home network is informed of the CoA.<br/>
(3) REGISTER HA - Requests the router on the home network to register the node as the HA of the network. Node receives a newly allocated IP address.<br/>
(4) MOVE new_ip new_port - Closes the node's current router connection and creates a new connection to the router specified at new_ip and new_port<br/>