import socket
import threading
import time


class RouterListener(threading.Thread):

    def __init__(self, TCP_IP, TCP_PORT, rtID, BUFFER_SIZE = 1024):
        super().__init__()

        self.TCP_IP = TCP_IP
        self.TCP_PORT = TCP_PORT
        self.BUFFER_SIZE = BUFFER_SIZE

        # Used by initRouters() in order to not create socket with itself
        self.rtID = rtID

        # Create bound socket to receive connections from Nodes, Home Agents, and other Routers
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.TCP_IP, self.TCP_PORT))
        self.socket.listen(5)

        # Stores home agent connection information when home agent registered with router
        self.homeAgent = ()

        # Used for determining next IP to allocate
        self.ipCount = 2

        # Stores dictionary mapping for other router IP addresses and their associated sockets
        self.routers = {}

        # Stores dictionary mapping of node IP addresses and their associated sockets
        self.nodes = {}

        print("[+] New server socket thread started for " + self.TCP_IP + ":" + str(TCP_PORT) + " with network address of " + self.rtID)

        self.start()


    def run(self):
        # Sleep for 5 seconds to allow for starting other routers
        time.sleep(5)

        # Set up sockets with other routers
        self.initRouters()

        print("Mobile IP Router : Waiting for connections from TCP clients...")
        while True:
            conn, addr = self.socket.accept()
            threading.Thread(target=self.clientListen, args=(conn, addr)).start()


    def clientListen(self, conn, addr):
        """
        Thread to listen for messages sent by clients/home agents and handle them according to their commands
        :param conn:      socket connection with client
        :param addr:      sent address of client
        :return:    boolean
        """
        while True:
            try:
                data = conn.recv(2048).decode()
                if data:
                    # Each field of message delineated by a space
                    splitData = data.split(' ')

                    # All messages must be at least 3 fields long
                    if(len(splitData) < 3):
                        print("Malformed packet received.")
                        continue

                    src = splitData[0]
                    dst = splitData[1]
                    payload = splitData[2]

                    # Handles if message intended for router
                    if dst == self.TCP_IP or dst == self.rtID:
                        # Allocate new IP address for node
                        if (payload == 'REGISTER'):
                            newIP = self.allocateIP(conn, addr, data)

                        # Triggered when the node is a registering HA
                        elif (payload == 'HA'):
                            self.setHA(conn, addr, data, newIP)

                        # Message sent between routers when they establish their connections with each other
                        elif ('ROUTER' in payload):
                            print("Initialized socket connection with " + payload)

                        # Sets the home agent's socket as the route to the home IP of the mobile node
                        elif (payload == 'SETHA'):
                            print('HA set for ' + splitData[3])
                            self.nodes[splitData[3]] = conn

                        # Triggered if command/msg type not recognized
                        else:
                            print("Server  data:" + str(data))
                            MESSAGE = 'Not a valid command'
                            conn.send(str.encode(MESSAGE))  # echo

                    # Handles if message is intended for a node
                    else:
                        self.handleMessage(splitData)

            except socket.timeout:
                print("Timing out now")
                conn.close()
                return False


    def allocateIP(self, conn, addr, data):
        """
        Allocates network IP for requesting node
        :param conn: socket descriptor for connection with node
        :param addr: address of sending node
        :param data: message sent by client in string format
        :return: returns IP address of newly connected node
        """

        print("Server received register command with data: " + str(data))
        splitIP = self.rtID.split('.')
        newIP = splitIP[0] + '.' + splitIP[1] + '.' + splitIP[2] + '.' + str(self.ipCount)
        self.nodes[newIP] = conn
        print("Connected Nodes: " + str(self.nodes.keys()))

        # Increment counter used to allocate IPs
        self.ipCount += 1

        # Sends allocated IP back to node in order for node to set its IP
        MESSAGE = 'Allocated IP is ' + newIP
        conn.send(str.encode(MESSAGE))  # echo
        return newIP


    def handleMessage(self, packet):
        """
        Decides whether destination is in router's network or to forward to another router
        :param packet:  packet contents represented as list of strings
        :return:        void
        """
        print("Handling Message")
        src = packet[0]
        dst = packet[1]
        payload = packet[2]
        conn = None
        haIP = None
        print("Source IP: " + src)
        print("Destination IP: " + dst)
        print("Payload: " + payload)

        dstSplit = dst.split('.')
        routerCheck = dstSplit[0] + '.' + dstSplit[1] + '.' + dstSplit[2] + '.1'

        # Check if destination address is located on this router's network
        if dst in self.nodes:
            print("Destination is on the network")

            # Had to make some messages 4 fields long (for registering CoA with Home Agent)
            # Looping through the fields allows for getting all fields rather than narrowing down to 3
            msg = ''
            for field in packet:
                msg += field
                msg += ' '

            print("Sending packet to " + dst + ": " + msg)
            nodeconn = self.nodes[dst]
            nodeconn.send(msg.encode())
            print("Packet sent")

        # Check if destination address is within network of another router and route appropriately
        elif (routerCheck in self.routers.keys()):
            print("Can be routed to router at " + routerCheck)

            # Had to make some messages 4 fields long (for registering CoA with Home Agent)
            # Looping through the fields allows for getting all fields rather than narrowing down to 3
            print("Packet length is " + str(len(packet)))
            msg = ''
            for field in packet:
                msg += field
                msg += ' '
            print("Routing message is " + msg)
            self.routers[routerCheck].send(msg.encode())

        # Unknown route to destination
        else:
            print("[-] Cannot send packet to destination")

    def isIP(self, ip):
        """
        Check if passed-in IP is a valid IP by splitting each octet and verifying it falls within standard range (0-255)
        :param ip: string representation of IP address
        :return: boolean
        """

        splitIP = ip.split('.')
        if (len(splitIP) != 4):
            return False
        for octet in splitIP:
            if (not octet.isdigit()):
                return False

            elif (int(octet) < 0 or int(octet) > 255):
                return False

        return True

    def setHA(self, conn, addr, data, ip):
        """
        Sets the connected node as the home agent of the network
        :param conn: socket descriptor for connection with node
        :param addr: address of sending node
        :param data: message sent by client in string format
        :return: void
        """
        print("Setting Home Agent")
        self.homeAgent = (ip, conn)
        print("New Home Agent: " + ip + ", " + str(conn.getsockname()))

    def initRouters(self):
        """
        Establishes socket connections to other routers specified within the routing table file.
        Sockets stored in dictionary:
            :key: Router network address
            :value: Socket to router
        :return: void
        """

        # Requires 'routingtable' file in same folder as where RouterListener is being run
        # Pulls out router IP information from file to make socket connection with other routers
        with open('routingtable') as fp:
            line = fp.readline()
            while line:
                splitLine = line.split(' ')

                # only establishes sockets to other routers; prevents creation of socket with self
                if (self.rtID != splitLine[0]):
                    self.routers[splitLine[0]] = self.routerSocket(splitLine[1], splitLine[2])
                    msg = str(splitLine[0]) + ' ' + str(splitLine[1]) + ' ' + 'ROUTER' + self.rtID
                    self.routers[splitLine[0]].send(msg.encode())

                line = fp.readline()

    def routerSocket(self, rIP, rPort):
        """
        Creates socket with other router specified by router IP and router Port
        :param rIP: IP of router with which to make socket
        :param rPort: Port of router with which to make socket
        :return: returns socket instance for connection to router
        """
        rconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        rconn.connect((rIP, int(rPort)))
        return rconn
