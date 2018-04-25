import socket
import queue
import threading
import errno
import time
from Packet import Packet

class Node(threading.Thread):

	def __init__(self, TCP_IP, TCP_PORT, IS_HA, BUFFER_SIZE=1024):
		super().__init__()
		self.routerIP = TCP_IP
		self.routerPort = TCP_PORT
		self.ip = "None"
		self.isHomeAgent = IS_HA
		self.bufferSize = BUFFER_SIZE
		#self.pktQueue = queue.Queue()
		self.responseQueue = queue.Queue()
		self.inputQueue = queue.Queue()
		self.pktQueue = queue.Queue()
		self.ackQueue = queue.Queue()
		self.conn = self.setConnection(self.routerIP, self.routerPort)
		self.firstStart = True
		self.regNodes = {}
		self.start()

	def run(self):
		# Register this node with the router
		pkt = Packet("None", self.routerIP, "REGISTER")
		print("Sending packet '" + pkt.toString() + "' to register with router")
		self.conn.send(pkt.toString().encode())
		print("Packet sent")
		ack = self.conn.recv(self.bufferSize).decode()
		print("ACK received: '" + ack + "'")
		tokens = ack.split(' ')
		self.ip = tokens[3]
		print("New IP Address: " + self.ip)
		self.firstStart = False

		if self.isHomeAgent:
			# Set home agent at router
			print("Home Agent Starting")
			pkt = Packet(self.ip, self.routerIP, "HA")
			print("Setting Home Agent")
			self.conn.send(pkt.toString().encode())
			#threading.Thread(target=self.homeAgentWorker).start()
		else:
			print("Mobile Node Starting")
			# threading.Thread(target=self.nodeWorker).start()
			threading.Thread(target=self.inputWorker).start()

		threading.Thread(target=self.recvWorker).start()
		threading.Thread(target=self.ackWorker).start()

		

	def sendWorker(self, pkt):
		"""
		:Description:	Thread that handles sending a packet to the router
		:Return:		void
		"""
		done = False
		while not done:
			try:
				print("Sending packet: '" + pkt.toString() + "'")
				self.conn.send(pkt.toString().encode())
				done = True
			except IOError:
				pass

	def recvWorker(self):
		while True:
			try:
				ack = self.conn.recv(self.bufferSize).decode()
				print("ACK Received: '" + ack + "'")
				self.ackQueue.put(ack)
			except IOError:
				pass
			time.sleep(0.5)

	def ackWorker(self):
		while True:
			if self.ackQueue.empty():
				continue
			else:
				ack = self.ackQueue.get()
				print("Processing ACK: '" + ack + "'")

				# If this node is a home agent, it needs to inspect the payload
				if self.isHomeAgent:
					tokens = ack.split(' ')
					src = tokens[0]
					dst = tokens[1]
					payload = tokens[2]

					# Add this node to the registration table if it requests to REGISTER
					"""if payload == "REGISTER":
						print("Registering " + src)
						self.regNodes.append(src)
						print(src + " Registered")
						pkt = self.ip + " " + src + " SETHA"
						self.conn.send(pkt.encode())"""

					# Add this node to the registration table if it requests to REGISTER
					# Register message: <CoA> <dst> <payload=REGISTER> <oldIP>
					print("Payload is " + payload)
					print("Length of tokens is " + str(len(tokens)))
					if (payload == "REGISTER"):
						print("Registering CoA " + src + " for node " + tokens[3])
						self.regNodes[tokens[3]] = src
						print(src + " Registered")
						splitIP = self.ip.split('.')
						rtIP = splitIP[0] + '.' + splitIP[1] + '.' + splitIP[2] + '.1'
						pkt = self.ip + " " + rtIP + " SETHA " + tokens[3]
						self.conn.send(pkt.encode())

					else:
						if (dst in self.regNodes.keys()):
							pkt = src + ' ' + self.regNodes[dst] + ' ' + payload
							self.conn.send(pkt.encode())
						else:
							print('[-] Destination not registered with home agent')

				time.sleep(0.5)

	def inputWorker(self):
		while True:
			msg = str(input("Enter a message or enter exit to quit: "))
			tokens = msg.split(' ')
			if msg == "exit":
				break
			elif tokens[0] == "MOVE":
				newIP = tokens[1]
				newPort = tokens[2]
				haIP = tokens[3]

				# Close and set new connection
				self.closeConnection()
				self.conn = self.setConnection(newIP, int(newPort))

				# Register with new router
				pkt = Packet(self.ip, self.routerIP, "REGISTER")
				print("Sending packet '" + pkt.toString() + "' to register with router")
				self.conn.send(pkt.toString().encode())
				print("Packet sent")

				# Receive the new IP address
				ack = self.conn.recv(self.bufferSize).decode()
				print("ACK received: '" + ack + "'")
				tokens = ack.split(' ')
				homeIP = self.ip
				self.ip = tokens[3]
				print("New IP Address: " + self.ip)

				haRegpkt = self.ip + ' ' + haIP + ' ' + "REGISTER" + ' ' + homeIP
				self.conn.send(haRegpkt.encode())

			else:
				src = tokens[0]
				dst = tokens[1]
				payload = tokens[2]
				pkt = Packet(src, dst, payload)
				threading.Thread(target=self.sendWorker, args=(pkt,)).start()


	# def homeAgentWorker(self):
	# 	"""
	# 	:Description:	Thread that handles the home agent protocol
	# 	:Return:		void
	# 	"""
	# 	self.payload = ""
	# 	self.ack = ""
	# 	rdata = []
	# 	rDataLen = 0
	# 	done = False
	# 	while True:
	# 		print("Waiting for packet")
	# 		self.ack = self.conn.recv(self.bufferSize).decode()
	# 		print("Packet received: " + self.ack)
	# 		#self.pktQueue.put(self.ack, block=True)	# Place self.ack in packet queue
	# 		rdata = self.ack.split(' ')
	# 		assert len(rdata) == 3
	# 		src = rdata[0]
	# 		dst = rdata[1]
	# 		payload = rdata[2]
	# 		if dst == self.ip:
	# 			print("Message received from " + src + ": " + self.ack)
	# 			# Add node to registered nodes list if it sent a register packet
	# 			if payload == "REGISTER":
	# 				print("Registering " + src)
	# 				self.regNodes.append(src)
	# 				print(src + " Registered")
	# 			# Send an ACK back to the node
	# 			self.payload = self.ip + " " + src + " " + "ACK"
	# 			self.conn.send(self.payload.encode())
	# 	self.closeConnection()

	def setConnection(self, newIP, newPort):
		"""
		:Description:	Sets up a new router connection
		:Param newIP: 	The IP address of the new router
		:Param newPort: The port of the new router
		:Return:		The new socket descriptor for the new router connection
		"""
		print("[+] Setting up new router connection")
		conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		conn.connect((newIP, newPort))
		self.routerIP = newIP
		self.routerPort = newPort
		print("[+] Now connected to router at IP: " + str(newIP) + ", Port: " + str(newPort))
		return conn

	def closeConnection(self):
		"""
		:Description:	Closes the current socket connection to the current router
		:Return:		void
		"""
		if self.conn:
			self.conn.close()
			self.conn = None

	def splitMsg(msg):
		tokens = msg.split(' ')
		tokensLen = len(tokens)
		assert tokensLen >= 3
		src = tokens[0]
		dst = tokens[1]
		payload = tokens[3]
		return (tokens[0], tokens[1], tokens[2])
