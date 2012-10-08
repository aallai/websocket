from socket import *
import re

class WebSocket() :
	
	'BSD-style interface to websockets'

	def __init__(self) :
		self.socket = socket()

	def listen(self, port=80) :
		self.socket.bind(('', port))
		self.socket.listen(5)
	 
	def accept(self) :
		conn, addr = self.socket.accept()
		hdr = self.parse_handshake(conn.recv(65535))	
		print hdr

	def parse_handshake(self, handshake) :

		'Returns a dictionary of header fields if handshake is valid'

		req = handshake.split('\n')[0]
		if not re.match(r'GET\s.+\sHTTP/1\.[1-9]', req) : 
			return {}

		hdr = dict(re.findall(r'([A-Za-z0-9]+):\s(.*)', handshake))
		
		
			
		
