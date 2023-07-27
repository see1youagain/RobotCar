#!/usr/bin/python
# -*- coding:utf8 -*-

import socket
import rospy
import threading

class ClientThread(threading.Thread):

    def __init__(self, clientsocket):
        threading.Thread.__init__(self)
        self.clientsocket = clientsocket
        self.MessageSend=""
        self.MessageReceive=""
        self.clientsocket.settimeout(1.0)  # 设置超时时间，单位为秒
        

    def run(self):
        while not rospy.is_shutdown():
            try:
                data = self.clientsocket.recv(1024).decode()
                session_id, msg = data.split(":")
                print("data: ", msg, " session: ", session_id)
            except socket.timeout:
                continue

    
    def SendMessage(self,msg):
        self.clientsocket.send(msg)

    def GetMessage(self):
        if len(self.MessageReceive)!=0 :
            msg = self.MessageReceive
            self.MessageReceive=""
            return msg
        else:
            return ""

def start_client():
    global socketThread
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('192.168.8.44', 8089))
    socketThread = ClientThread(s)
    socketThread.start()
    rospy.sleep(1)
    socketThread.SendMessage("clent2:this is client1")
    rospy.sleep(1)
    socketThread.SendMessage("clent2:this is client1,i am call for client1")
    
    while not rospy.is_shutdown():
        rospy.sleep(0.2)
    socketThread.SendMessage("client2:bye")
    socketThread.join()
    

if __name__ == "__main__":
    rospy.init_node('client2', anonymous=True)
    start_client()