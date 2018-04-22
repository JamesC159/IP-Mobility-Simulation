To execute:<br/>
(1) Open terminal Navigate to the Router directory<br/>
(2) Run 'python3 Router.py'<br/>
(3) Open another terminal and navigate to the Node directory<br/>
(4) Run 'python3 NodeDriver.py'<br/><br/>
Current messages supported between Node and Router:<br/>
(1) REGISTER - The router on the node's network registers the node with the HA of the network. The node receives a newly allocated IP address<br/>
(2) REGISTER FOREIGN - A foreign router, on a different network than the node's home network, registers the node with its HA. The node is given a Care of Address (new IP address on the foreign network). The node's HA is sent the Care of Address