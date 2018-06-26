import socket
import threading
import time
import sys

host = '192.168.0.109'
port = 5900

s = socket.socket()
s.connect((host,port))
print("connected with", host)

def receving(name):
    while True:
        ya = s.send(str.encode(name))
        print('Sent data: ', name)
        return ya





names = raw_input("Name")
message = raw_input(names + "->")
while True:
    receving(message)
    message = raw_input(names +"->")






