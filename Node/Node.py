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

		else:
			print("Mobile Node Starting")
			# threading.Thread(target=self.nodeWorker).start()
			threading.Thread(target=self.inputWorker).start()

		threading.Thread(target=self.recvWorker).start()
		threading.Thread(target=self.ackWorker).start()

		

	def sendWorker(self, pkt):
		"""
		Thread that handles sending a packet to the router
		:param pkt: message to be sent to router
		:return:    void
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
		"""
		Thread to listen for incoming messages from routers and place them in a queue to be handled by
		the ackWorker thread
		:return: void
		"""
		while True:
			# Checks if there are any messages to receive and adds them to the ackQueue
			try:
				ack = self.conn.recv(self.bufferSize).decode()
				print("ACK Received: '" + ack + "'")
				self.ackQueue.put(ack)
			except IOError:
				pass

			# Sleep for small delay to prevent queue from getting messed up by consecutive reads
			time.sleep(0.5)

	def ackWorker(self):
		"""
		Thread that retrieves messages from ackQueue and processes them according to their commands
		:return:    void
		"""
		while True:
			if self.ackQueue.empty():
				continue
			else:
				ack = self.ackQueue.get()
				print("Processing ACK: '" + ack + "'")

				# If this node is a home agent, inspect the payload
				if self.isHomeAgent:
					tokens = ack.split(' ')
					src = tokens[0]
					dst = tokens[1]
					payload = tokens[2]

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

					# Routes messages to their intended mobile node
					else:
						if (dst in self.regNodes.keys()):
							pkt = src + ' ' + self.regNodes[dst] + ' ' + payload
							print("Sending forwarded msg: " + pkt)
							self.conn.send(pkt.encode())
						else:
							print('[-] Destination not registered with home agent')

				time.sleep(0.5)

	def inputWorker(self):
		"""
		Thread that receives input from user and determines which actions to take based on the command
		:return: void
		"""
		while True:
			msg = str(input("Enter a message or enter exit to quit: "))
			tokens = msg.split(' ')
			if msg == "exit":
				break
			elif tokens[0] == "MOVE":
				newIP = tokens[1]
				newPort = tokens[2]
				haIP = tokens[3]

				# Close socket with home network router and set new connection to visiting network router
				self.closeConnection()
				self.conn = self.setConnection(newIP, int(newPort))

				# Register with new router
				pkt = Packet(self.ip, self.routerIP, "REGISTER")
				print("Sending packet '" + pkt.toString() + "' to register with router")
				self.conn.send(pkt.toString().encode())
				print("Packet sent")

				# Receive the new IP address from visiting network router
				ack = self.conn.recv(self.bufferSize).decode()
				print("ACK received: '" + ack + "'")
				tokens = ack.split(' ')
				homeIP = self.ip
				self.ip = tokens[3]
				print("New IP Address: " + self.ip)

				# Send msg to home agent to register home address with it
				haRegpkt = self.ip + ' ' + haIP + ' ' + "REGISTER" + ' ' + homeIP
				self.conn.send(haRegpkt.encode())

				# Need to start receiving thread for new socket connection
				threading.Thread(target=self.recvWorker).start()

			else:
				src = tokens[0]
				dst = tokens[1]
				payload = tokens[2]
				pkt = Packet(src, dst, payload)
				threading.Thread(target=self.sendWorker, args=(pkt,)).start()

	def setConnection(self, newIP, newPort):
		"""
		Sets up a new router connection
		:param newIP: 	The IP address of the new router
		:param newPort: The port of the new router
		:return:		socket descriptor for the new router connection
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
		Closes the current socket connection to the current router
		:return:		void
		"""
		if self.conn:
			self.conn.close()
			self.conn = None

	"""def splitMsg(msg):
		tokens = msg.split(' ')
		tokensLen = len(tokens)
		assert tokensLen >= 3
		src = tokens[0]
		dst = tokens[1]
		payload = tokens[3]
		return (tokens[0], tokens[1], tokens[2])
	"""
