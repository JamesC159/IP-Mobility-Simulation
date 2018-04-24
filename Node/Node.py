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
		self.regNodes = []
		self.start()

	def run(self):
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
			print("Home Agent Starting")
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
		print("Sending packet: '" + pkt.toString() + "'")
		self.conn.send(pkt.toString().encode())

	def recvWorker(self):
		while True:
			ack = self.conn.recv(self.bufferSize).decode()
			print("ACK Received: '" + ack + "'")
			self.ackQueue.put(ack)
			time.sleep(0.5)

	def ackWorker(self):
		while True:
			if self.ackQueue.empty():
				continue
			else:
				ack = self.ackQueue.get()
				print("Processing ACK: '" + ack + "'")
				if self.isHomeAgent:
					tokens = ack.split(' ')
					src = tokens[0]
					dst = tokens[1]
					payload = tokens[2]
					if payload == "REGISTER":
						print("Registering " + src)
						self.regNodes.append(src)
						print(src + " Registered")
						pkt = self.ip + " " + src + " ACK"
						self.conn.send(pkt.encode())
				time.sleep(0.5)

	def inputWorker(self):
		while True:
			msg = str(input("Enter a message or enter exit to quit: "))
			if msg == "exit":
				break
			tokens = msg.split(' ')
			assert len(tokens) >= 3
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
			self.conn.close
			self.conn = None

	def splitMsg(msg):
		tokens = msg.split(' ')
		tokensLen = len(tokens)
		assert tokensLen >= 3
		src = tokens[0]
		dst = tokens[1]
		payload = tokens[3]
		return (tokens[0], tokens[1], tokens[2])
