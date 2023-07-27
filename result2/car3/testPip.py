#!/usr/bin/python
# -*- coding:utf8 -*-
import socket
import threading
import rospy

IPV4="192.168.8.44"
PORT=8089

client_threads = []

class ServerThread(threading.Thread):

    def __init__(self, clientsocket):
        threading.Thread.__init__(self)
        self.clientsocket = clientsocket
        self.clientsocket.settimeout(1.0)  # 设置超时时间，单位为秒

    def run(self):
        while not rospy.is_shutdown():
            try:
                data = self.clientsocket.recv(1024).decode()
                session_id, msg = data.split(":")
                print("Received data: ", msg, " from session: ", session_id)
                if msg=="bye":
                    index = client_threads.index(self)
                    client_threads.pop(index)
                    break
                for client_thread in client_threads:
                    if client_thread != self:
                        client_thread.clientsocket.send(("Message from " + session_id + ": " + msg).encode())
            except socket.timeout:
                continue
def start_server():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((IPV4, PORT))
    serversocket.listen(5)

    while not rospy.is_shutdown():
        clientsocket, address = serversocket.accept()
        newthread = ServerThread(clientsocket)
        client_threads.append(newthread)
        newthread.start()



if __name__ == "__main__":
    start_server()