#!/usr/bin/python

from websocket import *

s = WebSocket()
s.listen(9000)
s = s.accept()

print s.recv()
