from socket import *
import copy

'''
BSD-style interface to websockets
'''

class WebSocket() :
	def __init__(self) :
		self.socket = socket()

	def listen(self, port=80) :
		self.socket.bind(('', port))
		self.socket.listen(5)
	 
	def accept(self) :
		conn, addr = self.socket.accept()
		print conn.recv(65536)			 
