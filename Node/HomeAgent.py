import socket
import threading

class HomeAgent(threading.Thread):
	
	def __init__(self, TCP_IP, TCP_PORT, BUFFER_SIZE = 1024):
		super().__init__()
		self.routerIP = TCP_IP
		self.routerPort = TCP_PORT
		self.ip = ""
		self.bufferSize = BUFFER_SIZE
		self.pktQueue = queue.Queue()
		self.conn = self.setConnection(self.routerIP, self.routerPort)
		self.firstStart = True
		self.start()

	def run(self):
		print("Home Agent Starting")
		threading.Thread(target = self.homeAgentWork).start()

	def homeAgentWork(self):
		"""
		:Description:	Thread that handles the Home Agent protocol
		:Return:		void
		"""
		if self.firstStart:
			print("Registering home agent with router")
		else:
			print("Doing stuff")

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