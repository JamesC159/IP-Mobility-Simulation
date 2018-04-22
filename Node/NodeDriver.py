from Node import Node

host = '127.0.0.1'
port = 2525

def main():
	node = Node(host, port)
	# connWrkThread = threading.Thread(target = connWrk, args=(host, port))
	# #pktWrkThread = threading.Thread(target = pktWrkr)
	# connWrkThread.start()
	# #pktWrkThread.start()
	# for thread in threading.enumerate():
	# 	if thread is mainThread:
	# 		continue
	# 	else:
	# 		thread.join()

# def connWrk(host, port):
# 	"""
# 	Thread for connection to router
# 	:param host: Socket descriptor for default router
# 	:param port: Port for default router
# 	:return: void 
# 	"""
# 	conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 	conn.connect((host, port))

# 	msg = ""
# 	msg = str(input("Enter a message or enter exit to quit: "))

# 	while msg != "exit":
# 		# Send amsg and recieve response
# 		conn.send(msg.encode())
# 		response = conn.recv(2000).decode()

# 		# Tokenize response
# 		data = response.split(' ')
# 		print("Router Response: " + response)

# 		# Process response based on msg sent
# 		if msg == "REGISTER":
# 			allocIP = data[3]
# 			print(allocIP)

# 		msg = str(input("Enter a message or enter exit to quit: "))

# 	conn.close()

# def pktWrkr():
# 	"""
# 	Processes packets from packet queue
# 	"""
# 	protoLen = 10
# 	routing = "routing".encode()
# 	homeAgent = "homeagent".encode()
# 	pkt = "".encode()
# 	localThreads = []
# 	while True:
# 		pkt = pktQueue.get(block = True)
# 		print("Got packet")
# 		protocol = pkt[:1]
# 		pktStr = pkt.decode()
# 		rThread = threading.Thread(target = routingWrkr, args = (pkt,))
# 		hThread = threading.Thread(target = homeAgntWrkr, args = (pkt,))
# 		if protocol == "R".encode():
# 			print("Routing pkt: " + pktStr)
# 			localThreads.append(rThread)
# 			rThread.start()
# 		elif protocol == "H".encode():
# 			print("Home Agent pkt: " + pktStr)
# 			localThreads.append(hThread)
# 			hThread.start()
# 		else:
# 			print("My packet:" + pktStr)
# 	for thread in localThreads:
# 		joinThread(thread)

# def routingWrkr(pkt):
# 		print("Routing Worker: " + pkt.decode())

# def homeAgntWrkr(pkt):
# 		print("Home Agent Worker: " + pkt.decode())

# def joinThread(thread):
# 	if not thread.is_alive():
# 		thread.join()

if __name__ == "__main__":
	main()
