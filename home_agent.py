import sys
import socket
import threading
import queue
import time

packetQueue = queue.Queue()
pktLock = threading.Lock()

def main():
	while True:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect(("localhost", 54321))
		s.send("Rrrouting".encode())
		time.sleep(0.5)
		s.send("Hhomeagent".encode())
		break	# Just break for now

if __name__ == "__main__":
	main()