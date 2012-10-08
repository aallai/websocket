from socket import *
import re

#
# TODO tls support
#

class WebSocket() :
	
	'BSD-style interface to websockets'

	def __init__(self) :
		self.socket = socket()

	def listen(self, port=80) :
		self.socket.bind(('', port))
		self.socket.listen(5)
	 
	def accept(self) :

		'Loop until a connection is established'

		while (True) :
			conn, addr = self.socket.accept()
			ret = self._parse_handshake(conn.recv(65535))	
		
			if ret is None :
				self._bad_handshake(conn)
				conn.close()
				continue
			
			resource, hdr = ret
			

	def _parse_handshake(self, handshake) :

		'Returns a resource name and dictionary of header fields if handshake is valid'

		req = handshake.split('\n')[0]
		m = re.match(r'GET\s.*(/.*)\sHTTP/1\.[1-9]', req)
		if not m : 
			return None

		# check header for required values as per rfc
		# using a liberal grammar here
		hdr = dict(re.findall(r'([^:\s]+):\s([^\r\n]*)', handshake))
		try :
			hdr['Host']

			if hdr['Upgrade'].lower() != 'websocket' :
				return None

			if hdr['Connection'].lower() != 'upgrade' :
				return None

			hdr['Sec-WebSocket-Key']

			if hdr['Sec-WebSocket-Version'] != '13' :
				return None
			
		except KeyError, e :
			return None		

		return (m.group(1), hdr)

	def _bad_handshake(self, socket) :
			
		'Send 400 Bad Request in response to bogus handshake'

		try :
			sock.sendall('HTTP/1.1 400 Bad Request\r\n\r\n')			
		except error :
			pass
			
		
