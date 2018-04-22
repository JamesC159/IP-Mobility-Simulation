import socket
import queue
import threading

class Node(threading.Thread):

	def __init__(self, TCP_IP, TCP_PORT, IS_HA, BUFFER_SIZE=1024):
		super().__init__()
		self.routerIP = TCP_IP
		self.routerPort = TCP_PORT
		self.ip = ""
		self.bufferSize = BUFFER_SIZE
		self.pktQueue = queue.Queue()
		self.conn = self.setConnection(self.routerIP, self.routerPort)
		self.isHomeAgent = IS_HA
		self.firstStart = True
		self.start()

	def run(self):
		print("Mobile Node Starting")
		if self.isHomeAgent:
			threading.Thread(target=self.homeAgentWork).start()
		else:
			threading.Thread(target=self.nodeWork).start()

	def nodeWork(self):
		"""
		:Description:	Thread that handles simple node protocol
		:Return:		void
		"""
		msg = str(input("Enter a message or enter exit to quit: "))
		while msg != "exit":
			tokens = msg.split(' ')
			tokensLen = len(tokens)
			if tokens[0] == "MOVE":
				# Connect to new router on a different network
				newIP = tokens[1]
				newPort = tokens[2]
				self.closeConnection()
				self.conn = self.setConnection(newIP, int(newPort))
			else: # Otherwise, send the message to the current router connection
				response = self.sendMsg(msg)
				responseTokens = response.split(' ')
				print("Router Response: " + response)
				if tokens[0] == "REGISTER":
					self.ip = responseTokens[3]
					print("New IP Address: " + self.ip)
				else:
					print("[-] Unsupported sent message. Nothing to process")
			msg = str(input("Enter a message or enter exit to quit: "))
		self.closeConnection()

	def homeAgentWork(self):
		"""
		:Description:	Thread that handles the home agent protocol
		:Return:		void
		"""
		msg = ""
		response = ""
		responseTokens = []
		if self.firstStart:
			print("Registering Home Agent")
			msg = "REGISTER HA"
			response = self.sendMsg(msg)
			print("Router Response: " + response)
			responseTokens = response.split(' ')
			self.ip = responseTokens[3]
			print("New IP Address: " + self.ip)
		self.closeConnection()


	def setConnection(self, newIP, newPort):
		"""
		:Description:	Sets up a new router connection
		:Param newIP: 	The IP address of the new router
		:Param newPort: The port of the new router
		:Return:		The new socket descriptor for the new router connection
		"""
		print("[+] Setting up new router connection")
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((newIP, newPort))
		self.routerIP = newIP
		self.routerPort = newPort
		print("[+] Now connected to router at IP: " + str(newIP) + ", Port: " + str(newPort))
		return s

	def closeConnection(self):
		"""
		:Description:	Closes the current socket connection to the current router
		:Return:		void
		"""
		if self.conn:
			self.conn.close
			self.conn = None

	def sendMsg(self, msg):
		self.conn.send(msg.encode())
		return self.conn.recv(self.bufferSize).decode()
