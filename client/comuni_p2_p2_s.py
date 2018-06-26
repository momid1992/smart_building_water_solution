import threading
import socket
import time, sys

host = '192.168.0.109'
port = 5900

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((host, port))
print('Connection successfu to: ', host)

def send_tcp_message(data, name):
    global times
    times = 1
    while True:
        if name == "Quite":
            reply = 'close'
            s.send(str(reply))
            s.close()
            #sys.exit()

        s.send(str(data +":" + name))
        time.sleep(times)
           # ok = s.recv(2048).decode('utf-8')
            #print('recving command: ',ok)
        time.sleep(times)
        #break



data = raw_input('Enter your name ->')
while True:
    name = raw_input(data + ":  ")
    str(data)
    str(name)
    send_tcp_message(data,name)

    break




s.close()
