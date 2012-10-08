from socket import *
import re
import base64
import hashlib

#
# TODO tls support
#

class WebSocket() :
	
	'BSD-style interface to websockets'

	# constants
	# constant used in handshake
	WS_GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

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
			self._establish(conn, hdr)		
			
			# TODO return new websocket?
			return 

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

			# length of base64 key must be 16 bytes
			key = hdr['Sec-WebSocket-Key']
			last_group = 0
			if key.endswith('=') :
				last_group = 3 - len(key[key.find('='):])

			if len(key.strip('=')) / 4 * 3 + last_group != 16 :
				return None

			if hdr['Sec-WebSocket-Version'] != '13' :
				return None
			
		except KeyError, e :
			return None		

		return (m.group(1), hdr)

	def _establish(self, socket, hdr) :

		'Respond to a handshake'

		accept = base64.b64encode(hashlib.sha1(hdr['Sec-WebSocket-Key'] + WebSocket.WS_GUID).digest())
		
		response = [
			'HTTP/1.1 101 Switching Protocols',
			'Upgrade: websocket',
			'Connection: Upgrade',
			'Sec-WebSocket-Accept: ' + accept,		
		]		
		
		socket.sendall('\r\n'.join(response) + '\r\n' * 2)

	def _bad_handshake(self, socket) :
			
		'Send 400 Bad Request in response to bogus handshake'

		try :
			socket.sendall('HTTP/1.1 400 Bad Request\r\n\r\n')			
		except error :
			pass
			
		
