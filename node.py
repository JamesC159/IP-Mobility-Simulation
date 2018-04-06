import sys
import socket
import argparse
import random
import struct

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-p", metavar = "<port>", type = int, dest = "port")
	args = parser.parse_args()
	port = args.port
	host = "localhost"
	firstStartUp = True
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# while True:
		
	# 	sock.listen(1)
	# 	client, addr = sock.accept()
	# 	print client.recv(1024)

if __name__ == "__main__":
	main()
