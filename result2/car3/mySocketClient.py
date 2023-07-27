#!/usr/bin/python
# -*- coding:utf8 -*-

import socket
import rospy
import threading
import Queue

class ClientThread(threading.Thread):

    def __init__(self, clientsocket):
        threading.Thread.__init__(self)
        self.clientsocket = clientsocket
        self.MessageSend=""
        self.MessageReceive=""
        self.clientsocket.settimeout(1.0)  # 设置超时时间，单位为秒
        self.msg_queue = Queue.Queue()
        

    def run(self):
        while not rospy.is_shutdown():
            try:
                data = self.clientsocket.recv(1024).decode()
                # print("data: ", msg, " id: ", id)
                self.msg_queue.put(data)
            except socket.timeout:
                continue


class mySocketClient():
    def __init__(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('192.168.8.44', 8089))
        self.socketThread = ClientThread(s)
        self.socketThread.start()
        self.rec_msg=""
        self.run_thread=threading.Thread(target=self.run)
        self.run_thread.start()
        
        
    def SendMessage(self,msg):
        self.socketThread.clientsocket.send(msg)
    
    def RefreshMessage(self):
        if self.rec_msg=="" and not self.socketThread.msg_queue.empty():
            self.rec_msg=self.socketThread.msg_queue.get()
    def GetMessage(self):
        res_msg=self.rec_msg
        self.rec_msg=""
        return res_msg

    def run(self):
        while not rospy.is_shutdown():
            self.RefreshMessage()
            rospy.sleep(0.2)
        self.socketThread.clientsocket.send("client2:bye")
        self.socketThread.join()
    

# if __name__ == "__main__":
#     rospy.init_node('client2', anonymous=True)
#     obj=mySocketClient()
#     while not rospy.is_shutdown():
#         rec_msg=obj.GetMessage()
#         if len(rec_msg) !=0 :
#             print("get msg")
    