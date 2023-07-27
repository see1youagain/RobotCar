#!/usr/bin/python
# -*- coding:utf8 -*-
import subprocess
import time
import signal
import os
import rospy
from std_msgs.msg import String
rospy.init_node('testCmd', anonymous=True)
global status,count
status=-1
count=0
roadPlan=""
roadPlan_pub = rospy.Publisher('/roadPlan_sub', String, queue_size=10)
def receiveRoadPlan(msg):
    global status,count
    print(msg.data)
    rospy.sleep(1)
    if msg.data=="startok":
        status=0
    if msg.data[0]=="w":
        count+=1
        if count<3:
            roadPlan=msg.data
            rospy.sleep(1)
            roadPlan_pub.publish(roadPlan+" ok")
        elif count==3:
            roadPlan=msg.data
            rospy.sleep(1)
            roadPlan_pub.publish(roadPlan+" ok")
            rospy.sleep(3)
            roadPlan_pub.publish("4:0|3:A|2:C|1:C")
        elif count>3:
            print("第二轮{}次".format(count-3))
            roadPlan=msg.data
            rospy.sleep(1)
            roadPlan_pub.publish(roadPlan+" ok")
        
    

roadPlan_sub=rospy.Subscriber('/roadPlan_pub', String, receiveRoadPlan,queue_size=10)

while not rospy.is_shutdown() and status==-1:
    roadPlan_pub.publish("start")
    rospy.sleep(1)
roadPlan_pub.publish("4:0|3:A|2:B|1:A")
rospy.sleep(1)
while not rospy.is_shutdown():
    rospy.sleep(1)

