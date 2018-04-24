import socket
import threading
from socketserver import ThreadingMixIn


# Multithreaded Python server : TCP Server Socket Thread Pool
class RouterListener(threading.Thread):
    # Multithreaded Python server : TCP Server Socket Program Stub

    def __init__(self, TCP_IP, TCP_PORT, BUFFER_SIZE = 1024):
        super().__init__()

        self.TCP_IP = TCP_IP
        self.TCP_PORT = TCP_PORT
        self.BUFFER_SIZE = BUFFER_SIZE
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.TCP_IP, self.TCP_PORT))
        self.socket.listen(5)
        self.homeAgent = ()
        self.ipCount = 2
        self.nodes = {}

        print("[+] New server socket thread started for " + self.TCP_IP + ":" + str(TCP_PORT))

        self.start()


    def run(self):
        print("Mobile IP Router : Waiting for connections from TCP clients...")

        while True:
            conn, addr = self.socket.accept()
            # conn.settimeout(60)
            threading.Thread(target=self.clientListen, args=(conn, addr)).start()


    def clientListen(self, conn, addr):
        """
        Add support for REGISTER HA to set the home agent for this network
        """
        while True:
            try:
                data = conn.recv(2048).decode()
                if data:
                    splitData = data.split(' ')

                    if(len(splitData) < 3):
                        print("Malformed packet received.")
                        continue

                    src = splitData[0]
                    dst = splitData[1]
                    payload = splitData[2]

                    if (payload == 'REGISTER'):

                        # Allocate new IP address for node
                        newIP = self.allocateIP(conn, addr, data)

                    elif (payload == 'FOREIGN'):
                        # Register CoA with home agent
                        self.registerHA(conn, addr, data)

                    # Triggered when the node is a registering HA
                    elif (payload == 'HA'):
                        self.setHA(conn, addr, data, newIP)

                    else:
                        print("Server  data:" + str(data))
                        MESSAGE = 'Not a valid command'
                        conn.send(str.encode(MESSAGE))  # echo

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
        :return: void
        """

        print("Server received register command with data: " + str(data))
        splitIP = self.TCP_IP.split('.')
        newIP = splitIP[0] + '.' + splitIP[1] + '.' + splitIP[2] + '.' + str(self.ipCount)
        self.nodes[newIP] = conn
        print("New dictionary: " + str(self.nodes.keys()))

        # Increment counter used to allocate IPs
        self.ipCount += 1
        print("New count is " + str(self.ipCount))

        # Sends allocated IP back to node in order for node to set its IP
        MESSAGE = 'Allocated IP is ' + newIP
        conn.send(str.encode(MESSAGE))  # echo
        return newIP


    def handleMessage(self, packet):
        """
        Decides whether destination is in router's network or to forward to another router
        :param packet: packet contents represented as list of strings
        :return: void

        TO BE IMPLEMENTED
        """
        print("Handling Message")
        pktLen = len(packet)
        assert pktLen == 3
        src = packet[0]
        dst = packet[1]
        payload = packet[2]
        builtPkt = " ".join(packet)
        conn = None
        haIP = None
        print("Source IP: " + src)
        print("Destination IP: " + dst)
        print("Payload: " + payload)
        if dst in self.nodes:
            print("Destination is on the network")
            print("Sending packet to " + dst + ": " + builtPkt)
            conn = self.nodes[dst]
            conn.send(builtPkt.encode())
            print("Packet sent")
        else:
            print("[-] Cannot send packet to destination")
        # if (destination in self.nodes): deliver via corresponding socket to destination node

        # elif (destination not in self.nodes and first 2 octets match another known router's IP):
        #   route message to matched router's socket

        # elif (destination in home agent list): route to visiting network's router

        # else: send error to source notify that destination does not exist        

    def isIP(self, ip):
        """
        Check if passed-in IP is a valid IP
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


    def registerHA(self, conn, addr, data):
        """
        Reaches out to home agent of home network to register CoA IP for proper tunneling
        :param conn: socket descriptor for connection with node
        :param addr: address of sending node
        :param data: message sent by client in string format
        :return: void

        TO BE IMPLEMENTED
        """

        print("Register HA.")
        pass

    def setHA(self, conn, addr, data, ip):
        """
        Sets the connected node as the home agent of the network
        :param conn: socket descriptor for connection with node
        :param addr: address of sending node
        :param data: message sent by client in string format
        :return: void

        TO BE IMPLEMENTED
        """
        print("Setting Home Agent")
        self.homeAgent = (ip, conn)
        print("New Home Agent: " + ip + ", " + str(conn.getsockname()))
