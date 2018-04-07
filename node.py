import sys
import socket
import argparse
import random
import struct
import threading
import queue

pktQueue = queue.Queue()
routingQueue = queue.Queue()
homeAgentQueue = queue.Queue()

def main():
	mainThread = threading.currentThread()
	listenThread = threading.Thread(target = listen)
	pktWrkThread = threading.Thread(target = pktWrkr)
	routingWrkrThread = threading.Thread(target = routingWrkr)
	homeAgntWrkrThread = threading.Thread(target = homeAgntWrkr)
	listenThread.start()
	pktWrkThread.start()
	routingWrkrThread.start()
	homeAgntWrkrThread.start()
	for thread in threading.enumerate():
		if thread is mainThread:
			continue
		else:
			thread.join()

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
	while True:
		pkt = pktQueue.get(block = True)
		print("Got packet")
		protocol = pkt[:1]
		if protocol == "R".encode():
			print("Routing: " + pkt.decode())
			routingQueue.put(pkt)
		elif protocol == "H".encode():
			print("Home Agent: " + pkt.decode())
			homeAgentQueue.put(pkt)

def routingWrkr():
	while True:
		pkt = routingQueue.get(block = True)
		print("Routing Worker: " + pkt.decode())

def homeAgntWrkr():
	while True:
		pkt = homeAgentQueue.get(block = True)
		print("Home Agent Worker: " + pkt.decode())

if __name__ == "__main__":
	main()
