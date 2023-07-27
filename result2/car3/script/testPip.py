#!/usr/bin/python
# -*- coding:utf8 -*-
import socket
import rospy
import mySocketClient

IPV4="192.168.8.44"
PORT=8089

client_threads = []

class ServerThread():

    def __init__(self):
        self.socketClient=mySocketClient.mySocketClient()

    def run(self):
        self.socketClient.SendMessage("car1:ok")
        while not rospy.is_shutdown():
            rospy.sleep(0.5)
            msg=self.socketClient.GetMessage()
            if(msg=="car2:ok"):
                print("car2启动成功")
                break
        min3_flag=1 if self.threeMinOKFlag==True else 0
        self.socketClient.SendMessage("car1:m:{}".format(min3_flag))
        self.cmd_pub.publish(15)
        self.secondCarStartFlag=True
        while not rospy.is_shutdown():
            socketMsg=self.socketClient.GetMessage()
            if len(socketMsg)!=0 :
                self.roadPlan_pub.publish(socketMsg)

if __name__ == "__main__":
    obj = ServerThread()
    obj.run()