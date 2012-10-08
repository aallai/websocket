from socket import *
from struct import *
import re
import base64
import hashlib
import copy

#
# TODO tls support
#

class WebSocketError(Exception) :
	pass

class WebSocket() :
	
	'BSD-style interface to websockets'

	# constant used in handshake
	WS_GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

	# states
	INITIAL, LISTENING, OPEN, CLOSED = xrange(4)	

	# opcodes
	CONT = 0x0 
	TEXT = 0x1
	BIN = 0x2
	# 0x3-7 reserved, non-control
	CLOSE = 0x8
	PING = 0x9
	PONG = 0xa
	# 0xb-f reserved, control	

	def __init__(self) :
		self._socket = socket()
		self._state = WebSocket.INITIAL 
		self._server = False

	def _assert_state(self, state, message='') :
		if self._state != state :
			raise WebSocketError(m) 

	def listen(self, port=80) :
		
		self._assert_state(WebSocket.INITIAL, 'Cannot listen while in state: ' + str(self._state))

		self._socket.bind(('', port))
		self._socket.listen(5)
		self._server = True
		self._state = WebSocket.LISTENING
	 
	def accept(self) :

		'Loop until a connection is established'

		self._assert_state(WebSocket.LISTENING, 'Cannot accept connections without calling listen()')

		while (True) :
			conn, addr = self._socket.accept()
			ret = self._parse_handshake(conn.recv(65535))	
		
			if ret is None :
				self._bad_handshake(conn)
				conn.close()
				continue
			
			resource, hdr = ret
			self._establish(conn, hdr)		
			socket = copy.deepcopy(self)
			socket._state = WebSocket.OPEN
			return socket 

	# TODO fragmenting?
	def send(self, frame, type_=None) :
		
		'Send a frame to the remote end. Type must be WebSocket.TEXT or WebSocket.BIN, TEXT is default.'

		self._assert_state(WebSocket.OPEN, 'Cannot send without establishing connection.')
		
		if type_ is None or type_ == WebSocket.TEXT :
			type_ = WebSocket.TEXT
			frame = frame.encode('utf-8')

		if type_ not in (WebSocket.TEXT, WebSocket.BIN) :
			raise TypeError, 'Frame type must be text or binary.'			
		
		# TODO handle sizes 
		size = len(frame)
		if size > 125 :
			raise ValueError, 'You need to implement variable size field.'


		fin_op = 1 << 7 | type_
		hdr = pack('BB', fin_op, size)
		self._socket.sendall(hdr + frame)			


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
			
		
