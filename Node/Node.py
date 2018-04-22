import socket
import queue
import threading

class Node(threading.Thread):

	def __init__(self, TCP_IP, TCP_PORT, BUFFER_SIZE=1024):
		super().__init__()
		self.routerIP = TCP_IP
		self.routerPort = TCP_PORT
		self.ip = ""
		self.bufferSize = BUFFER_SIZE
		self.pktQueue = queue.Queue()
		self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.msg = ""
		self.response = ""
		self.data = []
		self.start()

	def run(self):
		print("Mobile Node Starting")
		self.setConnection(self.routerIP, self.routerPort)
		threading.Thread(target=self.connWork).start()

	def connWork(self):
		"""
		Thread that handles communication between this node and a router
		"""
		self.msg = str(input("Enter a message or enter exit to quit: "))
		while self.msg != "exit":
			# Send a msg and receive response
			self.conn.send(self.msg.encode())
			self.response = self.conn.recv(2000).decode()

			# Tokenize response
			self.data = self.response.split(' ')
			print("Router Response: " + self.response)

			# Process response based on msg sent
			if self.msg == "REGISTER":
				self.ip = self.data[3]	# Since we registered with HA, we received a new IP address
				print(self.ip)
			elif self.msg == "REGISTER FOREIGN":
				self.ip = self.data[3] # Since we registered with FA, we received a new IP address
				print(self.ip)

			self.msg = str(input("Enter a message or enter exit to quit: "))

		self.conn.close()


	def setConnection(self, newIP, newPort):
		self.conn.connect((newIP, newPort))