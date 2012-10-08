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
		hdr = self._parse_handshake(conn.recv(65535))	

	def _parse_handshake(self, handshake) :

		'Returns a dictionary of header fields if handshake is valid'

		req = handshake.split('\n')[0]
		if not re.match(r'GET\s.+\sHTTP/1\.[1-9]', req) : 
			return {}

		# check header for required values as per rfc
		# using a liberal grammar here
		hdr = dict(re.findall(r'([^:\s]+):\s([^\r\n]*)', handshake))
		try :
			hdr['Host']

			if hdr['Upgrade'].lower() != 'websocket' :
				return {}

			if hdr['Connection'].lower() != 'upgrade' :
				return {}

			hdr['Sec-WebSocket-Key']

			if hdr['Sec-WebSocket-Version'] != '13' :
				return {}
			
		except KeyError, e :
			return {}		
		return hdr
		
			
		
