import sys
import socket
import random
import threading
import queue

pktQueue = queue.Queue()

def main():
	mainThread = threading.currentThread()
	listenThread = threading.Thread(target = listen)
	pktWrkThread = threading.Thread(target = pktWrkr)
	listenThread.start()
	pktWrkThread.start()
	for thread in threading.enumerate():
		if thread is mainThread:
			continue
		else:
			joinThread(thread)

def listen():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(("localhost", 54321))
	while True:
		s.listen(1)
		client, addr = s.accept()
		pkt = client.recv(1024)
		pktQueue.put(pkt)

def pktWrkr():
	protoLen = 10
	routing = "routing".encode()
	homeAgent = "homeagent".encode()
	pkt = "".encode()
	localThreads = []
	while True:
		pkt = pktQueue.get(block = True)
		print("Got packet")
		protocol = pkt[:1]
		pktStr = pkt.decode()
		rThread = threading.Thread(target = routingWrkr, args = (pkt,))
		hThread = threading.Thread(target = homeAgntWrkr, args = (pkt,))
		if protocol == "R".encode():
			print("Routing pkt: " + pktStr)
			localThreads.append(rThread)
			rThread.start()
		elif protocol == "H".encode():
			print("Home Agent pkt: " + pktStr)
			localThreads.append(hThread)
			hThread.start()
		else:
			print("My packet:" + pktStr)
	for thread in localThreads:
		joinThread(thread)

def routingWrkr(pkt):
		print("Routing Worker: " + pkt.decode())

def homeAgntWrkr(pkt):
		print("Home Agent Worker: " + pkt.decode())

def joinThread(thread):
	if not thread.is_alive():
		thread.join()

if __name__ == "__main__":
	main()
