# Python TCP Client A
import socket

host = '127.0.0.1'
port = 2525
BUFFER_SIZE = 2000
MESSAGE = str(input("tcpClientA: Enter message/ Enter exit: "))

tcpClientB = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpClientB.connect((host, port))

while MESSAGE != 'exit':
    tcpClientB.send(str.encode(MESSAGE))
    #data = tcpClientB.recv(BUFFER_SIZE).decode()
    #print(" Client2 received data:" + str(data))
    MESSAGE = str(input("tcpClientA: Enter message to continue/ Enter exit: "))

tcpClientB.close()